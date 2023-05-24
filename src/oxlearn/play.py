import abc
import logging

import oxlearn.board as _board

logger = logging.getLogger(__name__)

class IPlayer(abc.ABC):
    def __init__(self, symbol: _board.BoardSymbol, **kwargs):
        self.symbol = symbol

    @abc.abstractmethod
    def move(self, board: _board.Board) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def notify_win(self, board: _board.Board) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def notify_loss(self, board: _board.Board) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def notify_draw(self, board: _board.Board) -> None:
        raise NotImplementedError


def play_game(o_player: IPlayer, x_player: IPlayer) -> None:
    board = _board.Board(0)
    current_symbol = _board.BoardSymbol.first

    players = {
        _board.BoardSymbol.O: o_player,
        _board.BoardSymbol.X: x_player,
    }
    
    logger.info("New game: %s vs %s.", o_player.__class__.__name__, x_player.__class__.__name__)

    winner = None
    while not board.game_over:
        logger.info("%s turn.", current_symbol)
        logger.info("Current board: %d\n%s", board.encoded, board)
        next_pos = players[current_symbol].move(board)
        if next_pos is None:
            logger.info("%s concedes defeat.", current_symbol)
            winner = current_symbol.next
            break
        else:
            logger.info("%s plays %d.", current_symbol, next_pos)
            board += next_pos

            if board.game_over:
                winner = board.winner
            else:
                current_symbol = current_symbol.next

    logger.info("Final board: %d\n%s", board.encoded, board)
    if winner is None:
        logger.info("Game drawn.")
        o_player.notify_draw(board)
        x_player.notify_draw(board)
    else:
        logger.info("%s wins.", winner)
        players[winner].notify_win(board)
        players[winner.next].notify_loss(board)
