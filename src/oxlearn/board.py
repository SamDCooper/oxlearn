import enum
import logging
import typing


logger = logging.getLogger(__name__)

class BoardSymbol(enum.IntEnum):
    O = 1
    X = 2

    @property
    def next(self):
        return BoardSymbol.X if self is BoardSymbol.O else BoardSymbol.O

    def __str__(self):
        return "O" if self is BoardSymbol.O else "X"


BoardSymbol.first = BoardSymbol.O


class Board:
    _symbols = [None, BoardSymbol.O, BoardSymbol.X]
    representation_type: type = tuple[int, int, int, int, int, int, int, int, int]

    width = 3
    height = 3
    size = width * height

    _representation: representation_type
    _encoded: int

    _all_board_codes: list[int] = []

    @classmethod
    def all_positions(cls) -> typing.Iterable[int]:
        return range(cls.size)

    @classmethod
    def all_board_codes(cls) -> typing.Iterable[int]:
        if not cls._all_board_codes:
            for encoded in range(3**cls.size):
                board = Board(encoded)
                num_os = 0
                num_xs = 0
                for pos in cls.all_positions():
                    if board[pos] == BoardSymbol.O:
                        num_os += 1
                    elif board[pos] == BoardSymbol.X:
                        num_xs += 1
                difference = num_os - num_xs
                if difference == 1 or difference == 0:
                    cls._all_board_codes.append(encoded)

        for encoded in cls._all_board_codes:
            yield encoded

    @classmethod
    def encoded_to_representation(cls, encoded: int) -> representation_type:
        decoded = [0 for i in range(cls.width * cls.height)]
        for irow in range(cls.height):
            for icol in range(cls.width):
                v = encoded % 3
                decoded[icol + irow * cls.width] = v
                encoded = (encoded - v) // len(cls._symbols)
        return tuple(decoded)

    @classmethod
    def representation_to_encoded(cls, representation: representation_type) -> int:
        encoded = 0
        for irow in range(cls.height):
            for icol in range(cls.width):
                pos = icol + irow * cls.width
                encoded += representation[pos] * (len(cls._symbols) ** pos)
        return encoded

    @classmethod
    def from_representation(cls, representation: representation_type) -> "Board":
        board = Board(cls.representation_to_encoded(representation))
        board._representation = representation
        return board

    def __init__(self, encoded: int):
        self._encoded = encoded
        self._representation = None

    def __add__(self, pos: int) -> "Board":
        return Board(_movement[self.encoded][pos])

    def __sub__(self, other: "Board | int | None") -> "Board | int | None":
        if isinstance(other, Board):
            for pos, board_code in _movement[other.encoded].items():
                if board_code == self.encoded:
                    return pos
        elif isinstance(other, int):
            return Board(_backwards[self.encoded][other])
        return None

    def __getitem__(self, item: int) -> BoardSymbol:
        return self._symbols[self.representation[item]]

    def __hash__(self) -> int:
        return self.encoded

    def __eq__(self, other: "Board") -> bool:
        return self.encoded == other.encoded

    def __repr__(self) -> str:
        return f"Board({self.encoded})"

    def __str__(self) -> str:
        repr = self.representation
        rows = []
        for irow in range(self.height):
            row = []
            for icol in range(self.width):
                v = self[icol + irow * self.width]
                row.append("." if v is None else "O" if v == 1 else "X")
            rows.append(row)
        return "\n".join(" ".join(v for v in row) for row in rows)

    @property
    def encoded(self) -> int:
        return self._encoded

    @property
    def representation(self) -> representation_type:
        if self._representation is None:
            self._representation = self.encoded_to_representation(self.encoded)
        return self._representation

    @property
    def game_over(self) -> bool:
        return self.encoded in _game_over

    @property
    def winner(self) -> BoardSymbol | None:
        return _winner.get(self.encoded, None)

    @property
    def available_positions(self) -> typing.Iterable[int]:
        return _movement.get(self.encoded, {}).keys()


_game_over = set()
_winner = {}
_movement = {}
_backwards = {}


def _endgame_state(board: Board) -> tuple[bool, BoardSymbol]:
    win_lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [6, 4, 2],
    ]
    for win_line in win_lines:
        symbol = board[win_line[0]]
        if symbol is not None:
            if symbol == board[win_line[1]] and symbol == board[win_line[2]]:
                return True, symbol

    if 0 not in board.representation:
        return True, None

    return False, None


def _init():
    for board_code in Board.all_board_codes():
        board = Board(board_code)
        game_over, winner = _endgame_state(board)
        if game_over:
            _game_over.add(board.encoded)
            if winner is not None:
                _winner[board.encoded] = winner
        else:
            num_o = 0
            num_x = 0
            free_positions = []
            for pos in Board.all_positions():
                v = board[pos]
                if v == BoardSymbol.O:
                    num_o += 1
                elif v == BoardSymbol.X:
                    num_x += 1
                else:
                    free_positions.append(pos)
            current_player = (
                BoardSymbol.first if num_o == num_x else BoardSymbol.first.next
            )
            possible_moves = {}
            for pos in free_positions:
                repr = list(board.representation)
                repr[pos] = current_player
                new_board = Board.from_representation(repr)
                possible_moves[pos] = new_board.encoded
                if new_board.encoded not in _backwards:
                    _backwards[new_board.encoded] = {}
                _backwards[new_board.encoded][pos] = board_code
            _movement[board.encoded] = possible_moves
    logger.debug("Board movement: %s", _movement)
    logger.debug("Board backwards: %s", _backwards)
    logger.debug("Board winners: %s", _winner)
    logger.debug("Board gameover: %s", _game_over)

_init()
