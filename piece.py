import pygame
from game_constants import GREY, SQUARE_SIZE, CROWN


class Piece:
    """
    Piece class to build any piece of the board
    """
    PADDING = 10
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.get_pos()

    def get_pos(self):
        """
        Get current position
        """
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        """
        Current piece is converted to king
        """
        self.king = True

    def draw(self, win):
        """
        Draw each piece and the crown of any king
        """
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        # If the current piece is a king, put the crown image in the center of the piece
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def move(self, row, col):
        """
        Move a piece to a given row and column
        """
        self.row = row
        self.col = col
        self.get_pos()