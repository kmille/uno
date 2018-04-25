from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import os
from django.contrib.auth.models import User
from django.conf import settings
import pickle
import json
import random
from django.db.models import Q

from uno.logic.game import Game as RGame 
from uno.logic.util import Player

from .models import Game
from ipdb import set_trace

games = {}
PICKLE_FILE = "/tmp/pickle.dat"

def index(request):
    return render(request, "uno/index.html")


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid(): 
            form.save() # adds User object in the database
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user) #login user before redirect
            return redirect('lobby')
        else:
            return render(request, 'uno/signup.html', {'form': form}) # this forms objects has error messages
    
    form = UserCreationForm()
    return render(request, 'uno/signup.html', {'form': form})


@login_required
def lobby(request):
    # create a Game. if name is empty use a random name from settings.NAMES_FILE
    if request.method == 'POST':
        if "name" in request.POST:
            name = request.POST['name'].strip()
            if name == "":
                names_list = os.path.join(settings.BASE_DIR, "static", settings.NAMES_FILE)
                with open(names_list, "r") as f:
                    lines = f.readlines()
                name = lines[random.randint(0,len(lines))].strip()
            g = Game(creator=request.user, name=name)
            g.save()

    leaderboard = User.objects.all().order_by('-profile__wins')[:8]
    return render(request, "uno/lobby.html", { 'users': leaderboard })


@login_required
def get_lobby_games(request):
    # return json of all pending games if the logged in user is creator or participant
    # games (state=PENGING) or user=creator or user=player 
    games = Game.objects.filter(Q(state=0) | Q(creator=request.user) | Q(players=request.user) )
    return render(request, "uno/games.html", {'games': games})


@login_required
def join(request, game_id):
    # check if game exists and add user to the game
    try:
        game = get_object_or_404(Game, pk=game_id)
    except Game.DoesNotExist:
        return redirect("lobby")
    if request.user not in game.players.all():
        game.players.add(request.user)
    return redirect("lobby")


@login_required
def delete(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)
        # the game is only in the pickle if it was started before
        if game.state != 0: 
            del games[int(game_id)]
    except (Game.DoesNotExist):
        return JsonResponse({"msg":"error: Game does not exist"})
    except (KeyError):
        raise
    if game.creator == request.user:
        game.delete()
    return redirect("lobby")


def start(request, game_id):
    try:
        db_game = get_object_or_404(Game, pk=game_id)
        db_game.state = 1
        db_game.save()
    except Game.DoesNotExist:
        return JsonResponse({"msg":"error: Game does not exist"})
        print("ERROR: Game %d does not exist" % game_id)

    opponents = [Player(op.username, op.id) for op in db_game.players.all()]
    creator = Player(db_game.creator.username, db_game.creator.id)
    players = [ creator ] + opponents
    running_game = RGame(players)
    games[int(game_id)] = running_game # todo:schauen ob s schon da ist
    pickle.dump(games, open(PICKLE_FILE, "wb"))
    return redirect('play', game_id=game_id)



def play(request, game_id):
    try:
        game = get_object_or_404(Game, pk=game_id)
    except Game.DoesNotExist:
        return JsonResponse({"msg":"error: Game does not exist"})
    return render(request, "uno/play.html", {"game":game})

