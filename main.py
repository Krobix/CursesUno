import curses, random, math
#Uno game written in python using Curses for Performance task. Started 2/29/24

#To be shown at top of screen.
GAME_TITLE = """
 _   _               _ 
| | | |_ __   ___   | |
| | | | '_ \ / _ \  | |
| |_| | | | | (_) | |_|
 \___/|_| |_|\___/  (_)
"""

#String literal to be formatted to show specific cards. Uses keyword arguments for formatting
CARD_FORMAT = """_________
|       |
|       |
|       |
|{card_label}|
|       |
|       |
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
CARD_HEIGHT = 8

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
            i += 1

    def draw(self, window):
        #Given a curses Window object, draw a card on it. It's expected that the window is already the right size.
        window.erase()
        window.addstr(0, 0, CARD_FORMAT.format(card_label=self.label), curses.color_pair(self.color) | curses.A_BOLD)
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
            card_deck.append(Card(0, color, num))
        for num in range(1, 10):
            card_deck.append(Card(0, color, num))
            card_deck.append(Card(0, color, num))
        #action cards
        for t in (2, 3, 6, 7):
            card_deck.append(Card(t, color, -1))
            card_deck.append(Card(t, color, -1))

    #wild cards
    for i in (2, 4, 5):
        for j in range(0, 4):
            card_deck.append(Card(i, 0, -1))
            card_deck.append(Card(i, 0, -1))
    #The first card shouldnt be a wild
    while card_deck[len(card_deck)-1].color==0:
        random.shuffle(card_deck)

def game_finished():
    #TODO
    return False

def update_player_list(win):
    win.erase()
    win.addstr(0, 0, "PLAYER LIST:")
    y_offset = 5
    for p in players:
        pstring = f"Player {p.player_num}"
        if len(p.cards) > 1:
            pstring += f"\n{len(p.cards)} cards left"
        else:
            pstring += "\nHas uno!"
        win.addstr(y_offset, 0, pstring, curses.color_pair(p.color) | curses.A_BOLD)
        y_offset += 4
    win.refresh()

def status(msg, color, win):
    #Update "status" window (Message in middle of screen)
    win.erase()
    win.addstr(0, 0, msg, curses.color_pair(color) | curses.A_BOLD)
    win.refresh()

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
    #####CREATING WINDOWS
    #Argument order for newwin is: height, width, start y, start x
    title_win = curses.newwin(9, 26, 0, (screen_width//2)-(25//2))
    player_list_win = curses.newwin(screen_height, screen_width // 6)
    last_card_win = curses.newwin(CARD_HEIGHT+1, CARD_WIDTH+1, (screen_height//2)-(CARD_HEIGHT//2), (screen_width//2)-(CARD_WIDTH//2))
    status_msg_win = curses.newwin(screen_height//10, math.floor(screen_width*0.83), 15, screen_width//6)
    deck_scroll_status_win = curses.newwin(screen_height//10, math.floor(screen_width*0.83), screen_height-CARD_HEIGHT-1-screen_height//10, screen_width//6)
    player_deck_wins = [] #This will be filled in after
    #####################
    curses.curs_set(0)
    shown_cards_amount = math.floor((screen_width*0.8) / (CARD_WIDTH+3))
    card_win_start_x = (screen_width // 6) + 2
    for i in range(shown_cards_amount):
        window = curses.newwin(CARD_HEIGHT+1, CARD_WIDTH+1, screen_height-CARD_HEIGHT-2, card_win_start_x)
        player_deck_wins.append(window)
        card_win_start_x += CARD_WIDTH + 1
    #Main UI loop
    while not game_finished():
        #TODO
        title_win.addstr(0, 0, GAME_TITLE)
        title_win.refresh()
        update_player_list(player_list_win)
        #Display last card in deck
        card_deck[len(card_deck)-1].draw(last_card_win)




def main():
    #Real start of program; curses.wrapper() is called here
    global players
    print(WELCOME_MSG)
    generate_deck()
    players.append(Player(1, 0))
    players_amount = input()
    while not (players_amount.isdigit() and (int(players_amount) in range(2, 6))):
        print("Please enter an integer between 2-5:\n")
        players_amount = input()

    for i in range(int(players_amount)):
        players.append(Player(i+2, i+2))

    curses.wrapper(main_curses)

main()