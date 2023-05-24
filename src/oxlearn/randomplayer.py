import logging

from oxlearn import board as _board
from oxlearn.play import IPlayer as _IPlayer

logger = logging.getLogger(__name__)

class RandomPlayer(_IPlayer):
    def move(self, board: _board.Board) -> int:
        return random.choice(list(board.available_positions))

    def notify_win(self, board: _board.Board) -> None:
        pass

    def notify_loss(self, board: _board.Board) -> None:
        pass

    def notify_draw(self, board: _board.Board) -> None:
        pass
