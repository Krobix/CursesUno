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

YOUR_TURN_STATUS_MSG = "YOUR TURN STATUS MESSAGE PLACEHOLDER"

#Constants for card size
CARD_WIDTH = 9
CARD_HEIGHT = 8

#String where debug info is stored during execution of program. the ` key can be pressed to toggle it on screen
#If debug_enabled is True
debug_buffer = "DEBUG LOG"

#screen status
debug_showing = False
help_showing = False

#if debug menu should be available
debug_enabled = True


#global screen information variables
screen_height = 0
screen_width = 0

#game state variables
players = []
card_deck = []
turn_order = []
current_turn = 0 #Number of player whose turn it is (as an index of turn_order)
draw_num = 0 #Number of cards that next player has to draw.

#Exceptions- these are here to close the curses interface when certain actions are performed
class HelpInterrupt(Exception):
    pass

class DebugInterrupt(Exception):
    pass

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
        self.selected = False
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

    def draw(self, window, show_select=False):
        #Given a curses Window object, draw a card on it. It's expected that the window is already the right size.
        window.erase()
        if not show_select:
            window.addstr(0, 0, CARD_FORMAT.format(card_label=self.label), curses.color_pair(self.color) | curses.A_BOLD)
        else:
            #Show whether card has been selected or not (for player)
            selectcol = 0
            if self.selected:
                selectcol = 1
            window.addstr(0, (CARD_WIDTH//2)-1, "***", curses.color_pair(selectcol))
            window.addstr(1, 0, CARD_FORMAT.format(card_label=self.label), curses.color_pair(self.color) | curses.A_BOLD)
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

class CursesInterface:
    #Class that holds the different windows, etc.
    def __init__(self, stdscr):
        # Argument order for newwin is: height, width, start y, start x
        self.stdscr = stdscr
        self.title_win = curses.newwin(9, 26, 0, (screen_width // 2) - (25 // 2))
        self.player_list_win = curses.newwin(screen_height, screen_width // 6)
        self.last_card_win = curses.newwin(CARD_HEIGHT + 1, CARD_WIDTH + 1, (screen_height // 2) - (CARD_HEIGHT // 2), (screen_width // 2) - (CARD_WIDTH // 2))
        self.status_msg_win = curses.newwin(screen_height // 10, math.floor(screen_width * 0.83), 15, screen_width // 6)
        self.deck_scroll_status_win = curses.newwin(screen_height // 10, math.floor(screen_width * 0.83), screen_height - CARD_HEIGHT - 3 - (screen_height // 10), screen_width // 6)
        self.player_deck_wins = []  # This will be filled in after
        #####################
        shown_cards_amount = math.floor((screen_width * 0.8) / (CARD_WIDTH + 3))
        card_win_start_x = (screen_width // 6) + 2
        for i in range(shown_cards_amount):
            window = curses.newwin(CARD_HEIGHT + 2, CARD_WIDTH + 1, screen_height - CARD_HEIGHT - 3, card_win_start_x)
            self.player_deck_wins.append(window)
            card_win_start_x += CARD_WIDTH + 1
        self.displayed_card_range = [0, shown_cards_amount]
        self.selected_card = 0

    def update_player_list(self):
        win = self.player_list_win
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

    def status(self, msg, color):
        # Update "status" window (Message in middle of screen)
        self.status_msg_win.erase()
        self.status_msg_win.addstr(0, 0, msg, curses.color_pair(color) | curses.A_BOLD)
        self.status_msg_win.refresh()

    def display_player_cards(self, pl):
        #Given Player object pl, display their cards at bottom of screen based on scroll
        for c in self.player_deck_wins:
            c.erase()

        for i in range(self.displayed_card_range[0], self.displayed_card_range[1]):
            self.player_deck_wins[i - self.displayed_card_range[0]].erase()
            if i < len(pl.cards):
                pl.cards[i].draw(window=self.player_deck_wins[i-self.displayed_card_range[0]], show_select=True)
                self.player_deck_wins[i - self.displayed_card_range[0]].refresh()
        self.deck_scroll_status_win.erase()
        self.deck_scroll_status_win.addstr(0, 0, f"Showing cards {self.displayed_card_range[0]+1} to {min(self.displayed_card_range[1]+1, len(pl.cards))} of {len(pl.cards)}")
        self.deck_scroll_status_win.refresh()

        for c in self.player_deck_wins:
            c.refresh()

    def select_card(self, pl, card_ind):
        #Select card at given index in player's deck in the ui, and change scroll accordingly.
        self.selected_card = card_ind
        card_amount = self.displayed_card_range[1] - self.displayed_card_range[0]
        if card_ind >= len(pl.cards):
            self.selected_card = card_ind = len(pl.cards)-1
        elif card_ind < 0:
            self.selected_card = card_ind = 0
        if card_ind >= self.displayed_card_range[1]:
            self.displayed_card_range = [card_ind-card_amount+1, card_ind+1]
        elif card_ind < self.displayed_card_range[0]:
            self.displayed_card_range = [card_ind, card_ind+card_amount]
        for c in range(0, len(pl.cards)):
            if c==card_ind:
                pl.cards[c].selected = True
            else:
                pl.cards[c].selected = False

    def card_select_input(self, pl):
        #Allows the player to scroll through their cards using arrow keys and press enter to select a card.
        #Returns the index of the card selected. Infinite loop can be used here as return will break it
        while True:
            self.display_player_cards(pl)
            self.deck_scroll_status_win.keypad(True)
            key = self.deck_scroll_status_win.getkey()
            if key == "KEY_LEFT":
                self.select_card(pl, self.selected_card-1)
            elif key == "KEY_RIGHT":
                self.select_card(pl, self.selected_card+1)
            elif key=="`" and debug_enabled:
                raise DebugInterrupt
            elif key=="h":
                raise HelpInterrupt
            elif key=="\n":
                return self.selected_card

def debug(msg):
    #Adds msg to debug_buffer
    global debug_buffer
    debug_buffer += f"\n{msg}"

def show_help():
    #TODO
    pass

def debug_menu():
    #TODO
    pass

def show_debug():
    #TODO
    pass

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

def is_valid_card(card):
    #Checks a card to see if it can be played on top of last played card.
    #TODO: Remember to add stuff for checking if a draw card was placed and checking if played card is a draw card
    last_card = card_deck[len(card_deck)-1]
    if draw_num == 0:
        return (last_card.color==card.color) or (last_card.number==card.number) or (card.card_type in (1, 4, 5))
    else:
        if not (card.color==last_card.color or card.card_type in (1, 4, 5)) and (card.card_type in range(2, 6)):
            return False
        else:
            return True

def player_card_check(card, ui):
    #Uses is_valid_card and brings up color selection menu for wild cards
    #TODO
    return is_valid_card(card)

def ai_choose_card(pl):
    #Player object pl chooses card. If zero is returned, it chose to draw a card.
    card_scores = []
    draw_score = 0 # What the AI scores drawing a card as opposed to playing one
    color_amounts = {0:0,1:0,2:0,3:0,4:0,5:0,6:0}
    #Set color amounts
    for c in pl.cards:
        color_amounts[c.color] += 1
    #score cards
    for c in pl.cards:
        debug(f"Scoring card: color={c.color} type={c.card_type} number={c.number} label={c.label}")
        score = 0

        if not is_valid_card(c):
            score -= 1000
            draw_score += 1
        else:
            draw_score -= 100

        if c.card_type == 0:
            score += 15
        elif c.card_type in range(1, 6):
            score += 5
        else:
            score += 10

        if (draw_num > 0) and (c.card_type in range(2, 6)):
            score += 100

        score += color_amounts[c.color]

        debug(f"SCORE={score}")

        card_scores.append(score)

    highest_score = max(card_scores)
    card_or_draw = max(highest_score, draw_score)

    if card_or_draw==draw_score:
        return 0
    else:
        return card_scores.index(card_or_draw)


def take_turn(ui):
    #Takes current turn.
    global current_turn
    plnum = turn_order[current_turn]
    pl = players[plnum]
    if plnum==0:
        card_valid = False
        ui.status(YOUR_TURN_STATUS_MSG, 0)

        while not card_valid:
            played_card = ui.card_select_input(players[0])
            card_valid = player_card_check(pl.cards[played_card], ui)

        pl.play_card(played_card)

    else:
        #TODO
        pass

    current_turn += 1
    if current_turn >= len(turn_order):
        current_turn = 0


def game_finished():
    #TODO
    return False

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
    ##############################
    curses.curs_set(0)
    game_ui = CursesInterface(stdscr)
    #Main UI loop
    game_ui.select_card(players[0], 0)
    game_ui.title_win.addstr(0, 0, GAME_TITLE)
    game_ui.title_win.refresh()
    while not game_finished():
        #TODO
        game_ui.update_player_list()
        #Display last card in deck
        card_deck[len(card_deck)-1].draw(game_ui.last_card_win)
        #Display player cards
        take_turn(game_ui)
        game_ui.display_player_cards(players[0])




def main():
    #Real start of program; curses.wrapper() is called here
    global players
    print(WELCOME_MSG)
    generate_deck()
    players.append(Player(1, 0))
    turn_order.append(0)
    players_amount = input()
    while not (players_amount.isdigit() and (int(players_amount) in range(2, 6))):
        print("Please enter an integer between 2-5:\n")
        players_amount = input()

    for i in range(int(players_amount)):
        players.append(Player(i+2, i+2))
        turn_order.append(i+1)

    while not game_finished():
        try:
            curses.wrapper(main_curses)
        except HelpInterrupt:
            show_help()
        except DebugInterrupt:
            debug_menu()

main()