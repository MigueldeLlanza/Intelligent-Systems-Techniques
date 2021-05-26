import pygame
from game_constants import WHITISH, BROWN, WHITE, BLACK, ROWS, COLS, SQUARE_SIZE
from piece import Piece


class Board:
    """
    Board class to draw and modify the game board based on the moves selected by the player/AI
    """
    def __init__(self):
        self.board = []
        self.winner = None
        self.black_left = self.white_left = 12
        self.black_kings = self.white_kings = 0
        self.create_board()

    def create_board(self):
        """
        Creates the pieces of each color in its initial positions. A zero indicates that it is an empty square. Each
        piece is an object from the Piece class
        """
        self.board = [[0, Piece(0, 1, WHITE), 0, Piece(0, 3, WHITE), 0, Piece(0, 5, WHITE), 0, Piece(0, 7, WHITE)],
                      [Piece(1, 0, WHITE), 0, Piece(1, 2, WHITE), 0, Piece(1, 4, WHITE), 0, Piece(1, 6, WHITE), 0],
                      [0, Piece(2, 1, WHITE), 0, Piece(2, 3, WHITE), 0, Piece(2, 5, WHITE), 0, Piece(2, 7, WHITE)],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0],
                      [Piece(5, 0, BLACK), 0, Piece(5, 2, BLACK), 0, Piece(5, 4, BLACK), 0, Piece(5, 6, BLACK), 0],
                      [0, Piece(6, 1, BLACK), 0, Piece(6, 3, BLACK), 0, Piece(6, 5, BLACK), 0, Piece(6, 7, BLACK)],
                      [Piece(7, 0, BLACK), 0, Piece(7, 2, BLACK), 0, Piece(7, 4, BLACK), 0, Piece(7, 6, BLACK), 0]]

    def draw(self, win):
        """
        Draw each piece by calling the draw method from the Piece class
        """
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def draw_squares(self, win):
        """
        Draw squares
        """
        win.fill(BROWN)
        for row in range(ROWS):
            for col in range(row % 2, ROWS, 2):
                pygame.draw.rect(win, WHITISH, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def get_piece(self, row, col):
        """
        Get a piece corresponding to a given row and columns
        """
        return self.board[row][col]

    def evaluate_position(self, piece, d):
        """
        Function called by the heuristic function to compute the value of a piece depending on its current row position
        """
        if piece.color == BLACK:
            return abs(piece.row - d) / d + 1
        else:
            return - piece.row / d - 1


    def heuristics(self, difficulty):
        """
        Different heuristics are evaulated depending on the game difficulty selected
        """
        # For the easiest mode (1), the heuristic is just subtracting the black pieces to the white pieces
        if difficulty == 1:
            return self.black_left - self.white_left

        # In the medium difficulty, the heuristic is the same, except that the kings are also taken into account. In
        # particular, a king's value is 1.5 times a regular piece
        elif difficulty == 2:
            return self.black_left - self.white_left + (self.black_kings - self.white_kings) * 1.5

        # Finally, in the hard mode, the heuristic is a bit more complex. It takes into account the row position of
        # each piece. The closer to the top/bottom row, the higher is its value. However, a king always has the same
        # value, which is double than a regular piece. By doing this, the AI tends to move to put more pressure on its
        # opponent because a piece value increases linearly.
        elif difficulty == 3:
            d = 7
            king_points = 2

        evaluation = 0
        for row in self.board:
            for piece in row:
                if piece != 0:
                    if not piece.king:
                        evaluation += self.evaluate_position(piece, d)
                    elif piece.king:
                        if piece.color == BLACK:
                            evaluation += king_points
                        else:
                            evaluation -= king_points

        return evaluation

    def game_state(self, printed=False):
        """
        Checks the game state:
         - If a given player has zero pieces or no available moves, the game ends
        """
        if printed:
            print('White pieces:', self.white_left, '| White Kings:', self.white_kings)
            print('Black pieces:', self.black_left, '| Black Kings:', self.black_kings)
            return ''

        if self.white_left == 0 or not self.available_moves(WHITE):
            self.winner = 'White'
            return True, 'Black'

        if self.black_left == 0 or not self.available_moves(BLACK):
            self.winner = 'Black'
            return True, 'White'

        return False, self.winner

    def get_all_pieces(self, color):
        """
        Returns all the pieces of a given color
        """
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def move(self, piece, row, col):
        """
        Move a given piece to a selected row and column
        """
        # Replace value of the board where the piece was with a zero and the board value where the piece is moved (row
        # and column inputs) with the piece object that has been moved (piece.row and piece.col)
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if piece.color == WHITE and row == ROWS - 1 and not piece.king:
            piece.make_king()
            self.white_kings += 1
        elif piece.color == BLACK and row == 0 and not piece.king:
            piece.make_king()
            self.black_kings += 1
        else:
            pass

    def remove_piece(self, turn, valid_moves, selected, row, col):
        """
        Remove pieces if any jump has been made
        """
        # If there are available jumps, the pieces that will be removed are stored in 'erase'
        if valid_moves[1].get((row, col), 0) != 0:
            erase = valid_moves[1][(row, col)]
            # Loop over each piece that has to be removed
            for (erase_row, erase_col) in erase:
                # If the piece to be removed is a king and the piece that jumps over it is not, then this piece is
                # converted to king
                if self.get_piece(erase_row, erase_col).king and not selected.king:
                    selected.make_king()
                    # Update the number of black and white kings
                    if turn == WHITE:
                        self.white_kings += 1
                        self.black_kings -= 1
                    elif turn == BLACK:
                        self.white_kings -= 1
                        self.black_kings += 1

                # If both pieces are kings, then only the opponent's number of kings decreases
                elif self.get_piece(erase_row, erase_col).king and selected.king:
                    if turn == WHITE:
                        self.black_kings -= 1
                    elif turn == BLACK:
                        self.white_kings -= 1

                # Remove piece by setting it to '0'
                self.board[erase_row][erase_col] = 0

                # Update the overall number of pieces of each player
                if turn == WHITE:
                    self.black_left -= 1
                else:
                    self.white_left -= 1

    def available_moves(self, color):
        """
        Checks whether the current player has any available move
        """
        available = False
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    valid_moves = self.get_valid_moves(piece)
                    if valid_moves[0]:
                        available = True
        return available

    def get_valid_moves(self, piece):
        """
        Given a piece, it returns all the valid moves
        """
        # Get the pieces of the current player with available jumps
        available_jumps = self.available_jumps(piece.color)
        if available_jumps:
            if piece in available_jumps:
                # If there are available jumps and the current piece has available jumps, then its valid moves (if any)
                # are returned. This is to comply with the mandatory jump rule which states that a player must make a
                # jump if there is any available (i.e., mandatory jump)
                return self.get_moves(piece)
            elif piece not in available_jumps:
                # If there are available jumps but the given piece does not have, then an empty list and an empty
                # dictionary are returned, meaning that there are no moves for this piece
                return [], {}
        else:
            # If there are no available jumps, then the valid moves of the current piece (if any) are returned
            return self.get_moves(piece)

    def available_jumps(self, color):
        """
        Check whether there are available jumps for each piece of the current player
        """
        jumps = []
        for piece in self.get_all_pieces(color):
            moves = self.get_moves(piece)
            if moves[1]:
                jumps.append(piece)

        return jumps

    def get_moves(self, piece):
        """
        Get valid moves for a given piece
        """
        # Dictionary to store each valid move as keys, and as values each jumped opponents piece (if any)
        eaten = {}
        # Store valid moves
        total_moves = []

        # In both conditions the logic is the same. Given a location (row and column) of a piece and its color
        # it is searched if there is any available move (diagonally left/right and up/down depending on the color a
        # and whether it is a king or not). In the 'moves' list it is stored all available moves, and in the
        # 'jumped' list it is stored all the jumped pieces of the opponent. If the given piece is a king, it will be
        # searched any available movement on its left/right in both directions (up/down or, which is the same, 1/-1)
        if piece.color == WHITE or piece.king:
            total_moves_l = self.go_left(piece.row, piece.col, 1, eaten, piece, moves=[], jumped=[], previous=False)
            total_moves_r = self.go_right(piece.row, piece.col, 1, eaten, piece, moves=[], jumped=[], previous=False)
            total_moves += total_moves_l + total_moves_r

        if piece.color == BLACK or piece.king:
            total_moves_l = self.go_left(piece.row, piece.col, -1, eaten, piece, moves=[], jumped=[], previous=False)
            total_moves_r = self.go_right(piece.row, piece.col, -1, eaten, piece, moves=[], jumped=[], previous=False)
            total_moves += total_moves_l + total_moves_r

        # Store only the jump movements if the piece has any available
        if list(eaten.keys()):
            filtered_total_moves = [move for move in total_moves if move in list(eaten.keys())]
        else:
            filtered_total_moves = total_moves

        # Since 'None' is returned when there are no available movements in some direction (left/right), these are
        # are filtered from the total available moves list
        filtered_total_moves = [move for move in filtered_total_moves if move is not None]

        return filtered_total_moves, eaten

    def go_left(self, row, col, direction, eaten, piece, moves, jumped, previous):
        """
        Function that recursively searches along the left direction of a given piece. Several conditions are imposed
        to determine whether there is any available movement when moving leftwards
        """
        # Next row and column to explore. Depending on the color of the piece or whether it is a king or not, it will
        # explored the up-left squares and/or the down-left squares
        next_row = row + direction
        next_col = col - 1

        # If the next square to explore is within the board limits, then it is a valid square to explore a possible move
        if 0 <= next_row < ROWS and next_col >= 0 and next_col < COLS:
            # Get current piece
            current_piece = self.get_piece(row, col)
            # Get the piece of the square that is going to be explore
            next_piece = self.get_piece(next_row, next_col)

            # If the next square is empty and there has not been any previous jump, it is appended as a possible move
            if next_piece == 0 and not moves and not previous:
                moves.append((next_row, next_col))
                return moves

            # If in the next square there is an opponent's piece, a recursive call is made to explore further along
            # the left direction
            elif next_piece != 0 and next_piece.color != piece.color and not previous:
                self.go_left(next_row, next_col, direction, eaten, piece, moves, jumped, previous=True)
                return moves

            # If next square is empty and there has been a jump, it is appended as a possible move and also the piece
            # that has been captured
            elif next_piece == 0 and previous:
                jumped.append((row, col))
                eaten[(next_row, next_col)] = jumped.copy()
                moves.append((next_row, next_col))
                if not piece.king and current_piece.king:
                    return moves

            # If there is any available move it is returned the list with the moves
            elif moves:
                return moves

            # If there are no available moves, it is returned '[None]'
            else:
                return [None]

        # If the next square is out of the board bounds, then it is returned the moves appended
        elif moves:
            return moves

        # If the next square is out of bounds but no previous move has been appended, it is returned '[None]'
        else:
            return [None]

    def go_right(self, row, col, direction, eaten, piece, moves, jumped, previous=False):
        """
        Function that recursively searches along the right direction of a given piece. Several conditions are imposed
        to determine whether there is any available movement when moving rightwards. Note that this function has exactly
        the same structure as the 'go_left' function. Thus, the same comments made above apply here (just taking into
        account that the direction searched here is right instead of left)
        """
        next_row = row + direction
        next_col = col + 1

        if 0 <= next_row < ROWS and next_col >= 0 and next_col < COLS:
            current_piece = self.get_piece(row, col)
            next_piece = self.get_piece(next_row, next_col)

            # previous piece visited is not empty (i.e., we have encountered a piece form opponent before)
            if next_piece == 0 and not moves and not previous:
                moves.append((next_row, next_col))
                return moves

            elif next_piece != 0 and next_piece.color != piece.color and not previous:
                self.go_right(next_row, next_col, direction, eaten, piece, moves, jumped, previous=True)
                return moves

            elif next_piece == 0 and previous:
                jumped.append((row, col))
                eaten[(next_row, next_col)] = jumped.copy()
                moves.append((next_row, next_col))
                if not piece.king and current_piece.king:
                    return moves

            elif moves:
                return moves

            else:
                return [None]

        elif moves:
            return moves

        else:
            return [None]
