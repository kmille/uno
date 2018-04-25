# -*- coding: utf-8 -*-
import random 
import time
from uno.logic.util import Color, Player, Normal, Pull2, LoseTurn, Retour, ChangeColor, Pull4
from django.conf import settings

from ipdb import set_trace

class Game(object):
    def __init__(self, players):
        self.deck = list(self._init_deck())
        random.shuffle(self.deck)
        self.direction = True # True + | False -
        self.throw_counter = 0
        self._make_top()
        self.players = players 
        self.next = self.players[0]
        self.deal()
        self.turn_state = 1

    def _make_top(self):
        card = self.deck.pop(0)
        while not isinstance(card, Normal):
            self.deck.append(card)
            card = self.deck.pop(0)
        self.top = card
    
    def _find_card_for_id(self, card_id):
        try:
            return next(filter(lambda x: x.id == card_id, self.next.cards))
        except:
            return False
    
    def card_is_Pull4(self, card_id):
        card = self._find_card_for_id(card_id)
        return isinstance(card, Pull4)

    def check_turn(self, card_id, card=None):
        if not card:
            card = self._find_card_for_id(card_id)
        if not card: #clicked on the top card
            print("Card does not belong to you!")
            return False
        print("Comparing %s with %s" % (card, self.top))
        same_color = self.top.color == card.color
        same_type = isinstance(card, type(self.top))
        
        if isinstance(card, Pull4): # you can always use Pull4
            print("1", "True")
            return True
        
        if isinstance(self.top, Pull2):
            if self.turn_state == 4:
                print("1.1", isinstance(card, Pull2))
                return isinstance(card, Pull2)
            else:
                print("1.2", (same_color or same_type))
                return same_color or same_type

        if isinstance(self.top, Pull4):
            if self.turn_state == 4:
                return isinstance(card, Pull4)
            else:
                return same_color or same_type
       
#        if self.already_checked_in_this_turn and isinstance(self.top, Pull4): #same color works if we already have thrown
#           print("2", same_color)
#           return same_color
        
        if isinstance(card, ChangeColor): #ChangeColor works here always
            print("3", "True")
            return True
        elif isinstance(card, (Pull2, LoseTurn, Retour)): #same type or color
            print("4", (same_color or same_type))
            return same_color or same_type
        elif isinstance(card, Normal) and isinstance(self.top, Normal): # for normal card: same digit or collor
             same_digit = self.top.digit == card.digit
             print("5", (same_color or same_digit))
             return same_color or same_digit
        elif isinstance(card, Normal): # you have a normal card but on the top there is a special card

             print("6", same_color )
             return same_color 


    def throw(self):
        # try catch if deck is empty
        self.next.cards.append(self.deck.pop())
        if self.turn_state == 4:
            self.throw_counter -= 1

    def next_player(self):
        index_player = self.players.index((self.next))
        if self.direction:
            self.next = self.players[(index_player + 1) % len(self.players)]
        else:
            #print(index_player)
            index_player -= 1
            #print(index_player)
            index_player = len(self.players)-1 if index_player == -1 else index_player
            #print(index_player)
            self.next = self.players[index_player]


    def _can_play(self):
        print("Checking if you can play a card")
        if any([self.check_turn("card_id", card) for card in self.next.cards]):
            return True
        print("You can not play a card")
        return False

    def show_cards(self):
        print("Your cards (%d):" % (len(self.next.cards)))
        for i,card in enumerate(self.next.cards):
            print("  %d  %s" % (i,card))
    
    def _switch_color(self, card, color):
        #print("Which color do you want?")
        #for i,color in enumerate(Color):
        #    print("  %d  %s" % (i,color))
        #color_index = input("")
        #card.color = Color(int(color_index))
        card.color = Color(int(color))

    def _handle_special_cards(self, card, color=None):
        if isinstance(card, Pull4):
            self.throw_counter += 4
            print("Next player has to throw %d cards" % self.throw_counter)
            self._switch_color(card, color)
        if isinstance(card, Pull2):
            self.throw_counter += 2
            self.turn_state = 4
            print("Next player has to throw %d cards" % self.throw_counter)
        elif isinstance(card, LoseTurn):
            print("Next player will sit out")
            self.next_player()
        elif isinstance(card, Retour):
            print("Changing direction")
            self.direction = not self.direction
        elif isinstance(card, ChangeColor):
            self._switch_color(card, color)
        elif isinstance(card, Normal):
            self.throw_counter = 0 




    def turn(self):
        already_thrown=False
        print("\n\nIt's your turn %s" % self.next.name)
        print("Top: %s !!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % self.top)
        self.show_cards()
        if not self._can_play(already_thrown=False):
            if self.throw_counter > 0:
                for __ in range(self.throw_counter):
                    print("Throwing ...")
                    self.throw()
                    time.sleep(1)
                self.throw_counter = 0
                already_thrown=True
            else:
                print("Throwing ...")
                self.throw()
                time.sleep(1)
            self.show_cards()
            if not self._can_play(already_thrown=True):
                self.next_player()
                return 
        while 1:
            i = input("Your decision: ")
            try:
                card = self.next.cards[int(i)]
            except (IndexError, ValueError):
                print("Invalid input")
                break
            if(self.check_turn(card, already_thrown=already_thrown)):
                print("Playing card %s" % card)
                self.next.cards.remove(card)
                if len(self.next.cards) == 0:
                    print("You are a winner!!!")
                    exit()
                
                self._handle_special_cards(card)
                self.next_player()
                self.top = card
                return 
            else:
                print("You cant play this card.")


    def play_card(self, card_id, color=None):
        # return True if player wins the game
        card = self._find_card_for_id(card_id)
        #if card != self._find_card_for_id(self.tmp_card_id):
        self.next.cards.remove(card) 
        if len(self.next.cards) == 0:
            return True
        self._handle_special_cards(card, color)
        self.top = card
        return False

    def card_can_change_color(self, card_id):
        card = self._find_card_for_id(card_id)
        return isinstance(card, ChangeColor) or isinstance(card, Pull4)

    def deal(self):
        print("we are dealing")
        for player in self.players:
            for __ in range(settings.HAND_CARDS):
                player.cards.append(self.deck.pop())
            print("IDs for Player %s" % player.name)
            for card in player.cards:
                print("%s %s" % (card, card.id))


    def _init_deck(self):
        for color in Color:
            if color != Color.NONE:
                yield Normal(color, 0)
                for i in range(1,10):
                    yield Normal(color, i)
                    yield Normal(color, i)
                for i in range(2):
                    yield Pull2(color)
                    yield LoseTurn(color)
                    yield Retour(color)
        for __ in range(4): 
            yield Pull4()
            yield ChangeColor()


def main():
    g = Game()

if __name__ == '__main__':
    main()
