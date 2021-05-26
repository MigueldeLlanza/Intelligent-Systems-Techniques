import pygame
from board import Board
from game_constants import WHITE, BLACK, BLUE, RED, SQUARE_SIZE, CROWN


class Game:
    """
    Game class to update the game state based on the input of the player/AI and the current board state
    """
    def __init__(self, win, first_turn):
        self.win = win
        self.selected = None
        self.board = Board()
        self.first_turn = first_turn
        self.turn = self.first_turn
        self.valid_moves = []
        self.AI_activated = False
        self.winner = None
        self.end_game = False
        self.moved = False
        self.current = None
        self.is_king = False
        self.hint = True

    def reset(self, first_turn, AI_activated, hint):
        """
        Resets the main attributes of the game to the default values of
        """
        self.selected = None
        self.board = Board()
        self.board.white_left = self.board.black_left = 12
        self.board.white_kings = self.board.black_kings = 0
        self.turn = first_turn
        self.valid_moves = []
        self.AI_activated = AI_activated
        self.winner = None
        self.end_game = False
        self.moved = False
        self.current = None
        self.is_king = False
        self.hint = hint

    def update(self):
        """
        Update the board game information
        """
        self.board.draw(self.win)
        if self.selected:
            self.draw_selected_piece()
            if self.hint:
                self.draw_valid_moves()
        if self.end_game:
            print('GAME FINISHED. WINNER IS {}'.format(self.winner))

        pygame.display.update()

    def select(self, row, col):
        """Given a row and column selected:
            - If there is a piece of the player's color in the square selected, that piece is selected.
            - If the selected piece has no available movements, the function is recursively called so that a different
              piece with available movements is selected.
            - If the piece selected has available movements, the player can select where to move that piece.
            - If the player has made a jump, the select function is recursively called to check whether more jumps are
              available from that new position.
        """
        # Checks whether a valid piece (i.e., player's color) is currently selected
        if self.selected:
            # Boolean that says whether the current piece has available movements
            movement = self.move(row, col)
            if not movement:
                # If the current piece has no available movements and no jumps have been done, set the selected piece to
                # 'None' and make a recursive call to select a different piece
                if not self.current:
                    self.selected = None
                    self.select(row, col)

            else:
                old_valid = self.valid_moves[1].copy()
                piece = self.board.get_piece(row, col)
                self.valid_moves = self.board.get_valid_moves(piece)

                # If there are available movements, it is checked whether there are available jumps. If that is the
                # case, a recursive call is made to see whether there are more available jumps from that new position
                if self.valid_moves[1] and (row,col) in old_valid and self.selected.king == self.is_king:
                    piece = self.board.get_piece(row, col)
                    self.valid_moves = self.board.get_valid_moves(piece)
                    self.selected = piece
                    self.current = piece
                    self.moved = True
                    self.select(row, col)

                # If there are no available jumps, the piece is moved and the player's turn is over
                elif movement:
                    self.end_game, self.winner = self.board.game_state()
                    self.change_turn()
                    print('**************************************')
                    if self.turn == WHITE:
                        print('Turn: WHITE')
                    else:
                        print('Turn: BLACK')
                    print(self.board.game_state(True))
                    self.selected = None
                    self.current = None
                    self.moved = False

        # If there is no piece selected, the piece corresponding to the row and column is selected iff that piece
        # belongs to the player's turn
        elif not self.moved:
            piece = self.board.get_piece(row, col)
            if piece != 0 and piece.color == self.turn:
                self.selected = piece
                self.is_king = self.selected.king
                self.valid_moves = self.board.get_valid_moves(piece)

                return True

        # If a piece has been selected, it is stored its king status in its new position. The purpose of this is to
        # know whether a piece has been converted to king, which denies further moves (player's turn is over)
        elif self.moved:
            piece = self.board.get_piece(row, col)
            if piece != 0 and piece.color == self.turn and piece == self.current:
                self.selected = piece
                self.is_king = self.selected.king
                self.valid_moves = self.board.get_valid_moves(piece)
                return True
            else:
                return False

        return False

    def move(self, row, col):
        """
        Check whether there are available movements for a given board square selected
        """
        # If there are available moves, an opponents piece is removed if the current player has made any jump, and
        # the selected move is made by updating the board
        if self.selected and (row, col) in self.valid_moves[0]:
            self.board.remove_piece(self.turn, self.valid_moves, self.selected, row, col)
            self.board.move(self.selected, row, col)
        else:
            return False

        return True


    def draw_selected_piece(self):
        """
        The square of the current selected piece is drawn
        """
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill(RED)
        self.win.blit(s, (self.selected.col * SQUARE_SIZE, self.selected.row * SQUARE_SIZE))
        radius = SQUARE_SIZE // 2 - self.selected.PADDING
        pygame.draw.circle(self.win, self.selected.color, (self.selected.x, self.selected.y), radius)
        if self.selected.king:
            self.win.blit(CROWN, (self.selected.x - CROWN.get_width() // 2, self.selected.y - CROWN.get_height() // 2))

    def draw_valid_moves(self):
        """
        The squares corresponding to the available movements of the current selected piece are drawn
        """
        for move in self.valid_moves[0]:
            if move:
                row, col = move
                pygame.draw.rect(self.win, WHITE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                s = pygame.Surface((SQUARE_SIZE,SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(BLUE)
                self.win.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def change_turn(self):
        """
        Change the turn
        """
        if self.turn == WHITE:
            self.turn = BLACK
        else:
            self.turn = WHITE

    def current_piece(self, piece):
        """
        Get row and column of the current selected piece
        """
        row, col = piece.row, piece.col
        return row, col

    def current_board(self):
        """
        get the current game board
        """
        return self.board

    def AI_turn(self, board):
        """
        Given the board resulting from the move chosen by the AI, it is checked the current state of the game and
        the turn is changed
        """
        self.board = board
        self.end_game, self.winner = self.board.game_state()
        self.change_turn()
        print('**************************************')
        print('Turn: WHITE')
        print(self.board.game_state(True))
        self.update()

