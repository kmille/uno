import ipdb
import json
from uno.models import *
from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user
import pickle
from ipdb import set_trace
from .logic.game import Color
import giphypop
import random


PICKLE_FILE = "/tmp/pickle.dat"

def load(game_id):
    return pickle.load(open(PICKLE_FILE, "rb"))[game_id]


def save(game_id, game):
    games = pickle.load(open(PICKLE_FILE, "rb"))
    games[game_id] = game
    pickle.dump(games, open(PICKLE_FILE, "wb"))


def msg(msg):
    return json.dumps(dict(action="msg", content=msg))


def get_game_state(message, game_id):
    #set_trace()
    game = load(int(game_id))
    top = {'id': game.top.id, 'link': game.top.link }
    players = [{'name':p.name, 'cards': len(p.cards)}  for p in game.players]
    turn = game.next.name
    your_turn = message.user.id == game.next.id
    player = next(filter(lambda x: x.name == message.user.username, game.players))
    cards = [{'id':c.id, 'link': c.link }  for c in player.cards]
    return json.dumps(dict(action="game_state",top=top, turn=turn, your_turn=your_turn, players=players, cards=cards))

                
def handle_winner(message, userid, game_id):
    user = User.objects.get(pk=userid)
    user.profile.wins += 1
    user.save()
    Game.objects.get(pk=game_id).delete()
    g = giphypop.Giphy()
    gif_url = random.choice(list(g.search('success'))).media_url
    resp=dict(action="end_game", msg="%s won the game<br><img src='%s'>" % (user.username, gif_url))
    Group('game-%d' % game_id, channel_layer=message.channel_layer).send({'text':json.dumps(resp)})


@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send( {'accept':True})


@channel_session_user
def ws_receive(message):
    request = json.loads(message['text'])
    print("Request", request)
    game_id = int(request['game_id'])
    game = load(game_id)
    print("turn_state", game.turn_state)
    print("throw_counter", game.throw_counter)
    
    if request['action'] == "ping":
        Group('game-%d' % game_id, channel_layer=message.channel_layer).add(message.reply_channel)
        message.channel_session['game_id'] = game_id
        message.reply_channel.send( {'text':get_game_state(message, game_id)})
    elif request['action'] == "get_state":
        message.reply_channel.send( {'text':get_game_state(message, game_id)})
    elif request['action'] == "set_color":
        if game.turn_state != 3:
            message.reply_channel.send( {'text': msg("You cannnot change the color") })
        color = request['color']
        game.turn_state = 4 if game.card_is_Pull4(game.tmp_card_id) else 1
        if game.play_card(game.tmp_card_id, color):
            handle_winner(message, game.next.id, game_id) 
            return
        game.tmp_card_id = None
        Group('game-%d' % game_id, channel_layer=message.channel_layer).send(
                {'text':msg("%s wishes %s" % (game.next.name, Color(int(color)).name.lower()) ) })
        game.next_player()
        save(game_id, game)
        Group('game-%d' % game_id, channel_layer=message.channel_layer).send({'text':json.dumps(dict(action="reload_state"))})
    elif request['action'] == "move":
        card_id = int(request['id'])
        if game.check_turn(card_id):
            if game.card_can_change_color(card_id):
                message.reply_channel.send( {'text': json.dumps(dict(action="get_color"))})
                game.turn_state = 3
                game.tmp_card_id = card_id
                save(game_id, game)
                return 
            game.turn_state = 1
            if game.play_card(card_id): #sets turn_state to 4 if Pull2
                handle_winner(message, game.next.id, game_id)  
                return
            if game.throw_counter > 0:
                Group('game-%d' % game_id, channel_layer=message.channel_layer).send(
                    {'text':msg("%s has to throw %d cards" % (game.next.name, game.throw_counter) ) })
            game.next_player()
            save(game_id, game)
            Group('game-%d' % game_id, channel_layer=message.channel_layer).send({'text':json.dumps(dict(action="reload_state"))})
        else:
            save(game_id, game)
            message.reply_channel.send( {'text': msg("You cannot play this card") })
    elif request['action'] == "throw":
            if game.turn_state == 4:
                game.throw()
                game.turn_state = 2 if game.throw_counter == 0 else game.turn_state
                save(game_id, game)
                Group('game-%d' % game_id, channel_layer=message.channel_layer).send({'text':json.dumps(dict(action="reload_state"))})
                return
            elif game.turn_state != 1:
                message.reply_channel.send( {'text': msg("You already have thrown")})
                return
            game.throw()
            game.turn_state = 2
            save(game_id, game)
            Group('game-%d' % game_id, channel_layer=message.channel_layer).send({'text':json.dumps(dict(action="reload_state"))})
    elif request['action'] == "next":
        if game.turn_state == 4:
            if game.throw_counter != 0:
                message.reply_channel.send( {'text': msg("You still have to throw %d cards" % game.throw_counter)})
        elif game.turn_state == 2:
            game.next_player()
            game.turn_state = 1
            save(game_id, game)
            Group('game-%d' % game_id, channel_layer=message.channel_layer).send({'text':json.dumps(dict(action="reload_state"))})
        else:
            message.reply_channel.send( {'text': msg("You have to throw")})

        


@channel_session_user
def ws_disconnect(message):
    game_id = message.channel_session['game_id']
    Group('chat-%d' % game_id, channel_layer=message.channel_layer).discard(message.reply_channel)
