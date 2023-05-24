import json
import logging
import random

from oxlearn.board import Board as _Board
from oxlearn.board import BoardSymbol as _BoardSymbol
from oxlearn.play import IPlayer as _IPlayer

from oxlearn.training.dihedral import Dihedral as _Dihedral

logger = logging.getLogger(__name__)

class LearnPlayerBrain:
    # board : (canon, trans) such that trans * canon = board
    _canonical_board: dict[int, tuple[int, _Dihedral]]
    _board_valuation: dict[int, int]

    def __init__(self, input_file: str, output_file: str):
        self._canonical_board = {}
        self._board_valuation = {}
        self._output_file = output_file
        for board_code in _Board.all_board_codes():
            if board_code not in self._canonical_board:
                board = _Board(board_code)
                for t in _Dihedral:
                    trans_board = t * board
                    if trans_board.encoded not in self._canonical_board:
                        self._canonical_board[trans_board.encoded] = (board.encoded, t)
        try:
            with open(input_file, "r") as f:
                self._board_valuation = {}
                for k, v in json.load(f).items():
                    self._board_valuation[int(k)] = v
        except FileNotFoundError:
            pass
        logger.debug("Brain canonicals: %s", self._canonical_board)
        logger.debug("Board valuations: %s", self._board_valuation)

    def get_move(self, board_code: int) -> int:
        canon_code, trans = self._canonical(board_code)
        board = _Board(canon_code)
        
        options = {pos: self._board_value(self._next_board(board.encoded, pos)) for pos in board.available_positions}
        logger.info(" Canonical board: %d\n%s", board.encoded, board)
        logger.info(" Transformation: %s", trans)
        
        logger.info(" Options:")
        value_max = -0xFFFF
        next_pos = None
        board_max = None
        for pos, value in options.items():
            logger.info("  %d worth %.05f.", pos, value)
            if value >= value_max:
                value_max = value
                next_pos = pos
        logger.info(" Chosen %d.", next_pos)
        return trans * next_pos

    def learn(
        self, history: list[int], reward: float, learn_rate: float, decay_rate: float
    ) -> None:
        logger.info("Learning. reward = %.05f, learn_rate = %.05f, decay_rate = %.05f", reward, learn_rate, decay_rate)
        for board_code in reversed(history):
            canon_code, trans = self._canonical(board_code)
            valuation = self._board_value(canon_code)
            logger.info("Board %d value %.05f", canon_code, valuation)
            logger.info("+= %.05f * (%.05f * %.05f - %.05f)", learn_rate, decay_rate, reward, valuation)
            valuation += learn_rate * (decay_rate * reward - valuation)
            logger.info("= %.05f", valuation)
            reward = valuation
            self._board_valuation[canon_code] = valuation

    def save(self) -> None:
        with open(self._output_file, "w") as f:
            json.dump(
                {k: v for k, v in self._board_valuation.items() if v > 1e-5},
                f,
                indent=4,
            )

    def _board_value(self, canon_code: int) -> int:
        return self._board_valuation.get(canon_code, 0)

    def _canonical(self, board_code: int) -> tuple[int, _Dihedral]:
        return self._canonical_board[board_code]

    def _next_board(self, canon_code: int, pos: int) -> int:
        return self._canonical((_Board(canon_code) + pos).encoded)[0]


class TrainedPlayer(_IPlayer):
    def __init__(self, symbol: _BoardSymbol, brain: LearnPlayerBrain, **kwargs):
        super().__init__(symbol, **kwargs)
        self._brain = brain

    def move(self, board: _Board) -> int:
        return self._brain.get_move(board.encoded)

    def notify_win(self, board: _Board) -> None:
        pass

    def notify_loss(self, board: _Board) -> None:
        pass

    def notify_draw(self, board: _Board) -> None:
        pass

    @property
    def brain(self) -> LearnPlayerBrain:
        return self._brain


class LearnPlayer(TrainedPlayer):
    def __init__(
        self,
        symbol: _BoardSymbol,
        *,
        brain: LearnPlayerBrain,
        exploration_rate: float,
        learn_rate: float,
        decay_rate: float,
        **kwargs,
    ):
        super().__init__(symbol, brain, **kwargs)

        self._history = []

        self._reward_win = kwargs[
            "o_reward_win" if symbol == _BoardSymbol.O else "x_reward_win"
        ]
        self._reward_loss = kwargs[
            "o_reward_loss" if symbol == _BoardSymbol.O else "x_reward_loss"
        ]
        self._reward_draw = kwargs[
            "o_reward_draw" if symbol == _BoardSymbol.O else "x_reward_draw"
        ]

        self._exploration_rate = exploration_rate
        self._learn_rate = learn_rate
        self._decay_rate = decay_rate

    def move(self, board: _Board) -> int:
        if random.random() < self._exploration_rate:
            logger.info("Making random choice.")
            pos = random.choice(list(board.available_positions))
        else:
            logger.info("Making trained choice.")
            pos = super().move(board)
        self._history.append((board + pos).encoded)
        return pos

    def notify_win(self, board: _Board) -> None:
        logger.info("Learning from win.")
        self.brain.learn(
            self._history, self._reward_win, self._learn_rate, self._decay_rate
        )
        self._history = []

    def notify_loss(self, board: _Board) -> None:
        logger.info("Learning from loss.")
        self.brain.learn(
            self._history, self._reward_loss, self._learn_rate, self._decay_rate
        )
        self._history = []

    def notify_draw(self, board: _Board) -> None:
        logger.info("Learning from draw.")
        self.brain.learn(
            self._history, self._reward_draw, self._learn_rate, self._decay_rate
        )
        self._history = []
