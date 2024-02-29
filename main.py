import curses
#Uno game written in python using Curses for Performance task. Started 2/29/24

#String literal to be formatted to show specific cards. Uses keyword arguments for formatting
CARD_FORMAT = """_________
|       |
|{card_label}|
|_______|"""

#Constants for card size
CARD_WIDTH = 9
CARD_HEIGHT = 4

#####INTITIALIZING COLOR PAIRS
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
#############################

#String where debug info is stored during execution of program. the ` key can be pressed to toggle it on screen
#if debug_enabled is set to true under "input modes"
debug_buffer = "DEBUG LOG"

#screen status
debug_showing = False
help_showing = False

#input modes
card_select_enabled = True
debug_enabled = True
help_enabled = True

class Card:
    #Class for cards
    def __init__(self, card_type, color, number):
        """
        :param card_type: An integer. 0 is a regular numbered card, 1 is a wild, 2 is a +2, 3 is a +4, 4 is a wild+2,
        5 is a wild+4, 6 is a reverse, 7 is a skip.
        :param color: The card's number. Should be an int representing one of the color pairs between 2-5.
        :param number: Card's number between 0-9.
        """
        self.card_type = card_type
        self.color = color
        self.number = number
        self.create_label()

    def create_label(self):
        i = 0 #Used for padding- see below
        if self.card_type == 0:
            self.label = str(self.number)
        elif self.card_type == 1:
            self.label = "wild"
        elif self.card_type == 2:
            self.label = "+2"
        elif self.card_type == 3:
            self.label = "+4"
        elif self.card_type == 4:
            self.label = "wild+2"
        elif self.card_type == 5:
            self.label = "wild+4"
        elif self.card_type == 6:
            self.label = "reverse"
        elif self.card_type == 7:
            self.label = "skip"
        else:
            self.label = "???"
        #Pad the label out so that it's centered in the card
        while len(self.label) < (CARD_WIDTH - 2):
            if i % 2 == 0:
                self.label += " "
            else:
                self.label = " " +  self.label

    def draw(self, window):
        #Given a curses Window object, draw a card on it. It's expected that the window is already the right size.
        window.clear()
        window.addstr()

def main_curses(stdscr):
    #Entry point for curses
    pass

def main():
    #Real start of program; curses.wrapper() is called here
    curses.wrapper(main_curses)

main()