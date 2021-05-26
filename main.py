import pygame
import pygame_menu
from game_constants import WIDTH, HEIGHT, SQUARE_SIZE, WHITE, BLACK
from game import Game
from AI import AI


class Main:
    """
    Main class that contains:
        - Game menu (main menu, rules and game options)
        - Pygame initialization and display
        - Function to run the game
    """

    pygame.init()
    pygame.display.set_caption('Draughts')

    def __init__(self):
        self.FPS = 60
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.WIN = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.first = BLACK
        self.turn = [('Black', 0), ('White', 1)]
        self.game = Game(self.WIN, self.first)
        self.difficulties = [('Easy', 0), ('Medium', 1), ('Hard', 2)]
        self.difficulty = 1
        self.players = [('1 vs 1', 0), ('1 vs AI', 1)]
        self.AI_activated = False
        self.hints = [('Yes', 0), ('No', 1)]
        self.hint = True
        self.user_name_1 = 'Default'
        self.user_name_2 = 'Default'
        self.menus()

    def menus(self):

        global main_menu, game_over_menu

        # Game options menu
        game_menu = pygame_menu.Menu(self.WIDTH, self.HEIGHT, 'Game options', theme=pygame_menu.themes.THEME_BLUE)
        # Select the number of players (1 vs 1 or 1 vs AI)
        game_menu.add.selector('Players: ', self.players, onchange=self.select_players)
        # Choose the name of each player
        self.user_name_1 = game_menu.add.text_input('Player 1: ', default='Default')
        self.user_name_2 = game_menu.add.text_input('Player 2: ', default='Default')
        # Define the player that starts (default is black)
        game_menu.add.selector('Who starts?: ', self.turn, onchange=self.first_player)
        # Define difficulty (easy -default-, medium or hard)
        game_menu.add.selector('Difficulty: ', self.difficulties, onchange=self.set_difficulty)
        # Choose hint of available moves for each piece (default is active)
        game_menu.add.selector('Hint?: ', self.hints, onchange=self.set_hint)
        # Calls the function that runs the game
        game_menu.add.button('Play', self.run_game, True)

        # Game rules menu
        rules_menu = pygame_menu.Menu(self.WIDTH, self.HEIGHT, 'Rules', theme=pygame_menu.themes.THEME_BLUE)

        RULES = """The object is to eliminate all opposing checkers or to create a situation 
in which it is impossible for your opponent to make any move. Normally, the victory 
will be due to complete elimination. White moves first and play proceeds alternately. 
From their initial positions, checkers may only move forward. There are two types of 
moves that can be made, capturing moves and non-capturing moves. Non-capturing moves 
are simply a diagonal move forward from one square to an adjacent square. Capturing 
moves occur when a player "jumps" an opposing piece. This is also done on the diagonal 
and can only happen when the square behind (on the same diagonal) is also open. This 
means that you may not jump an opposing piece around a corner. 

On a capturing move, a piece may make multiple jumps. If after a jump a player is 
in a position to make another jump then he may do so. This means that a player may 
make several jumps in succession, capturing several pieces on a single turn. Forced 
Captures: When a player is in a position to make a capturing move, he must make a 
capturing move. When he has more than one capturing move to choose from he may take 
whichever move suits him. 

When a checker achieves the opponent's edge of the board (called the "king's row") 
it is crowned with another checker. This signifies that the checker has been made a 
king. The king now gains an added ability to move backward. The king may now also 
jump in either direction or even in both directions in one turn (if he makes multiple 
jumps). If the player gets an uncrowned checker on the king's row because of a capturing 
move then he must stop to be crowned even if another capture seems to be available. He
may then use his new king on his next move.
                
                """
        rules_menu.add.label(RULES, max_char=-1, font_size=18, font_color='Black')

        # Main menu
        main_menu = pygame_menu.Menu(self.WIDTH, self.HEIGHT, 'Main menu', theme=pygame_menu.themes.THEME_BLUE)
        # Got to game options menu
        main_menu.add.button('Play', game_menu)
        # Go to game rules menu
        main_menu.add.button('Rules', rules_menu)
        # Quit game
        main_menu.add.button('Quit', pygame_menu.events.EXIT)

        # While loop to run main menu
        while True:
            # Application events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    exit()

            # Main menu
            if main_menu.is_enabled():
                main_menu.mainloop(self.WIN)

            # Flip surface
            pygame.display.flip()


    def end_game_menu(self):
        """
        Menu that appears when the game has ended
        """
        # Game over menu
        game_over_menu = pygame_menu.Menu(self.WIDTH, self.HEIGHT, 'Game over', theme=pygame_menu.themes.THEME_DARK)

        # Depending on the game players, print the winner/loser
        if self.game.AI_activated and self.game.winner == 'White':
            WINNER = 'YOU WIN!'
            game_over_menu.add.label(WINNER, max_char=-1, font_size=70, font_color='Red')

        elif self.game.AI_activated and self.game.winner == 'Black':
            WINNER = 'YOU LOSE!'
            game_over_menu.add.label(WINNER, max_char=-1, font_size=70, font_color='Red')

        elif not self.game.AI_activated and self.game.winner == 'White':
            WINNER = 'THE WINNER IS ' + self.user_name_1.get_value().capitalize() + ' (White)'
            game_over_menu.add.label(WINNER, max_char=-1, font_size=70, font_color='Red')

        elif not self.game.AI_activated and self.game.winner == 'Black':
            WINNER = 'THE WINNER IS ' + self.user_name_2.get_value().capitalize() + ' (Black)'
            game_over_menu.add.label(WINNER, max_char=-1, font_size=70, font_color='Red')

        # Play again with the same settings
        game_over_menu.add.button('Play again', self.run_game, True, align=pygame_menu.locals.ALIGN_LEFT)
        # Go to main menu
        game_over_menu.add.button('Main menu', main_menu, align=pygame_menu.locals.ALIGN_LEFT)
        game_over_menu.mainloop(self.WIN)

    def pause_menu(self):
        """
        Menu when the game is paused
        """
        game_pause_menu = pygame_menu.Menu(self.WIDTH, self.HEIGHT, 'Pause', theme=pygame_menu.themes.THEME_BLUE)
        # Return to game
        game_pause_menu.add.button('Return to game', self.run_game, False)
        # Play again with the same settings
        game_pause_menu.add.button('Play again', self.run_game, True, align=pygame_menu.locals.ALIGN_LEFT)
        # Go to main menu
        game_pause_menu.add.button('Main menu', main_menu, align=pygame_menu.locals.ALIGN_LEFT)

        game_pause_menu.mainloop(self.WIN)

    def first_player(self, selected, value):
        """
        Defines the first player to move
        """
        if selected[0][0] == 'White':
            self.first = WHITE
            self.game.turn = WHITE
        else:
            self.first = BLACK
            self.game.turn = BLACK

    def select_players(self, selected, value):
        """
        Defines the type of game: '1 vs 1' or '1 vs AI'
        """
        if selected[0][0] == '1 vs AI':
            self.AI_activated = True
            self.game.AI_activated = True

        else:
            self.AI_activated = False
            self.game.AI_activated = False

    def set_difficulty(self, selected, value):
        """
        Defines the game difficulty
        """
        if selected[0][0] == 'Easy':
            self.difficulty = 1

        elif selected[0][0] == 'Medium':
            self.difficulty = 2

        elif selected[0][0] == 'Hard':
            self.difficulty = 3

    def set_hint(self, selected, value):
        """
        Sets whether hint is activated or not
        """
        if selected[0][0] == 'Yes':
            self.hint = True
            self.game.hint = True

        elif selected[0][0] == 'No':
            self.hint = False
            self.game.hint = False

    def get_row_col_from_mouse(self, pos):
        """
        Function that returns the row and column of the board (i.e., a square) given the current mouse position
        """
        x, y = pos
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE

        return row, col

    # Run Checkers
    def run_game(self, reset=False):
        """
        While loop to run the game
        """
        run = True
        clock = pygame.time.Clock()

        global main_menu, game_over_menu
        # AI object from the AI class that will be the AI player
        AI_player = AI(self.difficulty)

        # Disable main menu to show the checkers game (board and pieces)
        main_menu.disable()
        main_menu.full_reset()

        # Show some game statistics in console while playing
        print('*****')
        if self.game.turn == WHITE:
            print('Turn: WHITE')
        else:
            print('Turn: BLACK')
        print(self.game.board.game_state(True))

        while run:
            # Set the FPS
            clock.tick(self.FPS)
            # If reset is True, the game options are reset
            if reset:
                self.game.reset(self.first, self.AI_activated, self.hint)
                reset = False

            # If the game has ended, the game over menu is called
            if self.game.end_game:
                self.end_game_menu()

            # Since AI is always playing blacks, if it is the black turn and the it is a '1 vs AI' game, the
            # minimax alpha beta pruning is called to select its move
            if self.game.turn == BLACK and self.game.AI_activated:
                board = self.game.current_board()
                eval, ai_move = AI_player.minimax_alpha_beta(board, self.difficulty, self.game, float('-inf'), float('inf'))
                self.game.AI_turn(ai_move)

            # Human player's turn
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False

                    # If the mouse button is clicked, piece selection is on
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        row, col = self.get_row_col_from_mouse(pos)
                        self.game.select(row, col)

                    # If the escape key is pressed, the pause menu is called
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.pause_menu()

            # Update game
            self.game.update()
        # Quit game
        pygame.quit()

if __name__ == '__main__':
    Main()
