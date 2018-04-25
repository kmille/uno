from enum import Enum
import random

class Color(Enum):
    YELLOW = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    NONE = -1

class Player(object):
    def __init__(self, name, uid):
        self.cards = []
        self.name = name
        self.id = uid

class Card(object):
    def __init__(self, color):
        self.id = random.randrange(0,100000000000)
        self.color = color

class Normal(Card):
    def __init__(self, color, digit):
        super().__init__(color)
        self.digit = digit
        self.link = "%s-%d.png" % (Color(self.color).name.lower(), self.digit)

    def __repr__(self):
        return "%s %d" % (self.color.name, self.digit)

class Pull2(Card):
    def __init__(self, color):
        super().__init__(color)
        self.link = "%s-%s.png" % (Color(self.color).name.lower(), "Pull2" )
    
    def __repr__(self):
        return "2 ZIEHEN (%s)" % self.color.name

class LoseTurn(Card):
    def __init__(self, color):
        super().__init__(color)
        self.link = "%s-%s.png" % (Color(self.color).name.lower(), "LooseTurn")
    
    def __repr__(self):
        return "AUSSETZEN (%s)" % self.color.name

class Retour(Card):
    def __init__(self, color):
        super().__init__(color)
        self.link = "%s-%s.png" % (Color(self.color).name.lower(), "Retour")
    
    def __repr__(self):
        return "RICHTUNGSWECHSEL (%s)" % self.color.name


class ChangeColor(Card):
    def __init__(self):
        super().__init__(Color.NONE)
        self.link = "ChangeColor.png" 
    
    def __repr__(self):
        return "Wünscher: %s" % self.color.name

class Pull4(Card):
    def __init__(self):
        super().__init__(Color.NONE)
        self.link = "Pull4.png"
    
    def __repr__(self):
        return "4 ZIEHEN! und %s " % self.color.name
