from copy import deepcopy
from game_constants import WHITE, BLACK


class AI:
    """
    AI class to build the AI based on the minimax alpha beta pruning and the difficulty selected
    """
    def __init__(self, difficulty):
        self.difficulty = difficulty

    def minimax_alpha_beta(self, position, depth, max_player, alpha, beta):
        """
        Minimax alpha beta pruning algorithm that allows the AI to choose the best possible move based on the
        heuristics defined in the Board class
        """
        # Get the current game state
        end_game, winner = position.game_state()
        # If the depth reached is zero or there is a winner, the algorithm returns the corresponding evaluation for a
        # certain node
        if depth == 0 or winner != None:
            return position.heuristics(self.difficulty), position

        # Check whether it is the max player's turn (IA)
        if max_player:
            # Set maximum evaluation to minus infinite
            max_eval = float('-inf')
            best_move = None
            # Loop over all possible moves for the black player (IA)
            for move in self.get_all_moves(position, BLACK):
                # Recursive call to get the evaluation of each node of the min player
                evaluation = self.minimax_alpha_beta(move, depth - 1, False, alpha, beta)[0]

                # Compare the maximum evaluation with the evaluation obtain by the recursive call
                if max_eval < evaluation:
                    max_eval = evaluation
                    best_move = move
                    # Get maximum between alpha and the maximum evaluation
                    alpha = max(alpha, max_eval)
                    # If beta is less than or equal to alpha, pruning is made and it is returned the maximum evaluation
                    # along with the corresponding move that gets to that maximum value
                    if beta <= alpha:
                        break

            return max_eval, best_move

        # For the min player (human) it is an analogue process to the max player
        else:
            min_eval = float('inf')
            best_move = None
            for move in self.get_all_moves(position, WHITE):
                evaluation = self.minimax_alpha_beta(move, depth - 1, True, alpha, beta)[0]

                if min_eval > evaluation:
                    min_eval = evaluation
                    best_move = move
                    beta = min(beta, min_eval)
                    if beta <= alpha:
                        break

            return min_eval, best_move


    def get_all_moves(self, current_board, color):
        """Function that returns all the possible board configuration as a consequence of each of the possible moves
         that the AI can make
         """
        self.update_board = current_board
        boards = []
        # Loop over each piece from the player selected
        for piece in current_board.get_all_pieces(color):
            # Compute each possible board configuration for each possible move that a piece can make
            new_board = self.board_state(piece, self.update_board, simulated_boards=[])
            boards.extend(new_board)

        return boards

    def board_state(self, piece, current_board, simulated_boards, was_king=False, moved=False):
        """
        Given a piece, get its valid moves and the board state assocaited to each move
        """
        valid_moves = current_board.get_valid_moves(piece)
        is_king = piece.king
        # If a piece has been moved and there are still valid moves available (i.e., jumps available) and the piece has
        # not be converted to king during that move, then each of the available moves are evaluated. If that piece has
        # been moved, then each of the available moves are evaluated.
        if (moved and list(valid_moves[1].keys()) and was_king == is_king) or not moved:
            # Loop over each of the valid moves for that piece
            for move in valid_moves[0]:
                # Make a deep copy of the current board (temporal board)
                temp_board = deepcopy(current_board)
                # Get the piece from the deep copied board (temporal piece)
                temp_piece = temp_board.get_piece(piece.row, piece.col)
                # Remove jumped pieces (if any) from the deep copied board
                temp_board.remove_piece(BLACK, valid_moves, temp_piece, move[0], move[1])
                # Move temporal piece from the temporal board
                temp_board.move(temp_piece, move[0], move[1])

                # If a move has a jump available, then a recursive call is made to evaluate further possible moves
                if move in list(valid_moves[1].keys()):
                    simulated_boards += self.board_state(temp_piece, temp_board, simulated_boards, piece.king, True)

                # If a move has no further available moves, it is appended the temporal board as a possible board
                # configuration that the AI can evaluate
                else:
                    simulated_boards.append(temp_board)

            return list(set(simulated_boards))

        else:
            return [current_board]
