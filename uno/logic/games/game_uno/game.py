import random 
import time
from util import Color, Player, Normal, Pull2, LoseTurn, Retour, ChangeColor, Pull4
HAND_CARDS = 3

class Game(object):
    def __init__(self):
        self.deck = list(self._init_deck())
        random.shuffle(self.deck)
        self.direction = True # True + | False -
        self.throw_counter = 0
        self.top = self.deck.pop()
        #self.players = [Player("S1"), Player("S2"), Player("S3")]
        self.players = [Player("Hans"), Player("Peter")]
        self.next = self.players[0]
        self._deal()
        while 1:
            self.turn()

    def _check_turn(self, card, already_thrown):
        print("Comparing %s with %s with alreay_thrown %s" % (card, self.top, already_thrown))
        same_color = self.top.color == card.color
        same_type = isinstance(card, type(self.top))
        
        if isinstance(card, Pull4): # you can always use Pull4
            print("1", "True")
            return True
        
        if isinstance(self.top, Pull2):
            if already_thrown:
                print("1.1", (same_color or same_type))
                return same_color or same_type
            else:
                print("1.2", isinstance(card, Pull2))
                return isinstance(card, Pull2)

        if isinstance(self.top, Pull4):
            if already_thrown:
                return same_color or same_type
            else:
                return isinstance(card, Pull4)
        
        if already_thrown and isinstance(self.top, Pull4): #same color works if we already have thrown
            print("2", same_color)
            return same_color
        
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


    def _can_play(self, already_thrown=False):
        print("Checking if you can play a card")
        if any([self._check_turn(card, already_thrown) for card in self.next.cards]):
            return True
        print("You can not play a card")
        return False

    def show_cards(self):
        print("Your cards (%d):" % (len(self.next.cards)))
        for i,card in enumerate(self.next.cards):
            print("  %d  %s" % (i,card))
    
    def _switch_color(self, card):
        print("Which color do you want?")
        for i,color in enumerate(Color):
            print("  %d  %s" % (i,color))
        color_index = input("")
        card.color = Color(int(color_index))

    def _handle_special_cards(self, card):
        if isinstance(card, Pull4):
            self.throw_counter += 4
            print("Next player has to throw %d cards" % self.throw_counter)
            self._switch_color(card)
        if isinstance(card, Pull2):
            self.throw_counter += 2
            print("Next player has to throw %d cards" % self.throw_counter)
        elif isinstance(card, LoseTurn):
            print("Next player will sit out")
            self.next_player()
        elif isinstance(card, Retour):
            print("Changing direction")
            self.direction = not self.direction
        elif isinstance(card, ChangeColor):
            self._switch_color(card)


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
            if(self._check_turn(card, already_thrown=already_thrown)):
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



    def _deal(self):
        for player in self.players:
            for __ in range(HAND_CARDS):
                player.cards.append(self.deck.pop())


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
