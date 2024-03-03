import curses, random
#Uno game written in python using Curses for Performance task. Started 2/29/24

#String literal to be formatted to show specific cards. Uses keyword arguments for formatting
CARD_FORMAT = """_________
|       |
|{card_label}|
|_______|"""

#Welcome and help messages
WELCOME_MSG = """
Hello! Welcome to Uno. Yu will be playing the Uno card game in the terminal with 2-5 computer players. If you want to know how to play,
you can press the h key any time after leaving this screen to view the instructions. Please note that this game requires a terminal that 
supports color. Do NOT resize the terminal while playing. For now, please enter the amount of computer players
 that you want to play against (between 2-5):\n
"""

#Constants for card size
CARD_WIDTH = 9
CARD_HEIGHT = 4

#String where debug info is stored during execution of program. the ` key can be pressed to toggle it on screen
debug_buffer = "DEBUG LOG"

#screen status
debug_showing = False
help_showing = False

#input modes
card_select_enabled = True
debug_enabled = True
help_enabled = True

#global screen information variables
screen_height = 0
screen_width = 0

#game state variables
players = []
card_deck = []

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
        debug(f"Created Card object with card_type={str(card_type)} color={str(color)} number={str(number)} label={str(self.label)}")

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
                self.label = " " + self.label

    def draw(self, window):
        #Given a curses Window object, draw a card on it. It's expected that the window is already the right size.
        window.clear()
        window.addstr(CARD_FORMAT.format(card_label=self.label), curses.color_pair(self.color))
        window.refresh()

class Player:
    #Class for players (Computer and Human)
    def __init__(self, player_num, color):
        self.player_num = player_num
        self.color = color
        self.cards = []
        for i in range(7):
            self.draw_card()

    def draw_card(self):
        #Draw random card
        self.cards.append(card_deck.pop(0))

    def play_card(self, card_num):
        #Method to play card for both computer and human players.
        #Does not check for validity or make actions happen.
        card_deck.append(self.cards.pop(card_num))

def debug(msg):
    #Adds msg to debug_buffer
    global debug_buffer
    debug_buffer += f"\n{msg}"

def generate_deck():
    #Generate card deck at start of game
    global card_deck
    debug("Generating deck")
    for color in range(2, 6):
        for num in range(0, 10):
            card_deck.append(Card(0, color, num))
        for num in range(1, 10):
            card_deck.append(Card(0, color, num))
        for t in (2, 3, 6, 7):
            card_deck.append(Card(t, color, -1))

    for i in (2, 4, 5):
        for j in range(0, 4):
            card_deck.append(Card(i, 1, -1))

    random.shuffle(card_deck)

def main_curses(stdscr):
    #Entry point for curses
    global screen_height, screen_width
    screen_height, screen_width = stdscr.getmaxyx()
    #####INTITIALIZING COLOR PAIRS
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    #############################


def main():
    #Real start of program; curses.wrapper() is called here
    global players
    print(WELCOME_MSG)
    generate_deck()
    players_amount = input()
    while not (players_amount.isdigit() and (int(players_amount) in range(2, 6))):
        print("Please enter an integer between 2-5:\n")
        players_amount = input()

    for i in range(int(players_amount)):
        players.append(Player(i+1, i+1))

    curses.wrapper(main_curses)

main()