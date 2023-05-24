import enum

from oxlearn.board import Board as _Board
from oxlearn.training.permutation import Permutation as _Permutation


# Dihedral group of order 8 is the symmetry group of the square.
# A square has eight symmetries:
# e = no action.
# r = rotate 90 degrees clockwise.
# s = reflect about vertical axis |.
# The remaining five are combinations of r and s. Note that s^2 = e and r^4 = e,
# and rs = sr^-1.
# r^2 = rotate 180 degreees..
# r^3 = rotate 90 degrees anticlockwise.
# sr = reflect about diagonal axis \.
# sr^2 = reflect about horizontal axis -.
# sr^3 = reflect about diagonal axis /.
# Here a square is represented as the grid
# 0 1 2
# 3 4 5
# 6 7 8
# and symmetries represented as permutations of the 9 element list.


class Dihedral(enum.Enum):
    e = (0, (0, 1, 2, 3, 4, 5, 6, 7, 8))
    r = (1, (6, 3, 0, 7, 4, 1, 8, 5, 2))
    r2 = (2, (8, 7, 6, 5, 4, 3, 2, 1, 0))
    r3 = (3, (2, 5, 8, 1, 4, 7, 0, 3, 6))
    s = (4, (2, 1, 0, 5, 4, 3, 8, 7, 6))
    sr = (5, (8, 5, 2, 7, 4, 1, 6, 3, 0))
    sr2 = (6, (6, 7, 8, 3, 4, 5, 0, 1, 2))
    sr3 = (7, (0, 3, 6, 1, 4, 7, 2, 5, 8))

    _permutation: _Permutation
    _index: int

    def __init__(self, index, args):
        self._index = index
        self._permutation = _Permutation(*args)

    def __mul__(self, other: "Dihedral | _Board | any") -> "Dihedral | _Board | any":
        if isinstance(other, _Board):
            return _Board.from_representation(
                tuple(
                    other.representation[i] for i in ~self.permutation * tuple(range(9))
                )
            )
        if isinstance(other, Dihedral):
            return self._product[other._index]
        else:
            return self.permutation * other

    def __invert__(self) -> "Dihedral":
        return self._inverse
    
    def __str__(self):
        return self.name
        
    @property
    def permutation(self) -> _Permutation:
        return self._permutation


Dihedral.e._product = [
    Dihedral.e,
    Dihedral.r,
    Dihedral.r2,
    Dihedral.r3,
    Dihedral.s,
    Dihedral.sr,
    Dihedral.sr2,
    Dihedral.sr3,
]
Dihedral.e._inverse = Dihedral.e

Dihedral.r._product = [
    Dihedral.r,
    Dihedral.r2,
    Dihedral.r3,
    Dihedral.e,
    Dihedral.sr3,
    Dihedral.s,
    Dihedral.sr,
    Dihedral.sr2,
]
Dihedral.r._inverse = Dihedral.r3

Dihedral.r2._product = [
    Dihedral.r2,
    Dihedral.r3,
    Dihedral.e,
    Dihedral.r,
    Dihedral.sr2,
    Dihedral.sr3,
    Dihedral.s,
    Dihedral.sr,
]
Dihedral.r2._inverse = Dihedral.r2

Dihedral.r3._product = [
    Dihedral.r3,
    Dihedral.e,
    Dihedral.r,
    Dihedral.r2,
    Dihedral.sr,
    Dihedral.sr2,
    Dihedral.sr3,
    Dihedral.s,
]
Dihedral.r3._inverse = Dihedral.r

Dihedral.s._product = [
    Dihedral.s,
    Dihedral.sr,
    Dihedral.sr2,
    Dihedral.sr3,
    Dihedral.e,
    Dihedral.r,
    Dihedral.r2,
    Dihedral.r3,
]
Dihedral.s._inverse = Dihedral.s

Dihedral.sr._product = [
    Dihedral.sr,
    Dihedral.sr2,
    Dihedral.sr3,
    Dihedral.s,
    Dihedral.r3,
    Dihedral.e,
    Dihedral.r,
    Dihedral.r2,
]
Dihedral.sr._inverse = Dihedral.sr

Dihedral.sr2._product = [
    Dihedral.sr2,
    Dihedral.sr3,
    Dihedral.s,
    Dihedral.sr,
    Dihedral.r2,
    Dihedral.r3,
    Dihedral.e,
    Dihedral.r,
]
Dihedral.sr2._inverse = Dihedral.sr2

Dihedral.sr3._product = [
    Dihedral.sr3,
    Dihedral.s,
    Dihedral.sr,
    Dihedral.sr2,
    Dihedral.r,
    Dihedral.r2,
    Dihedral.r3,
    Dihedral.e,
]
Dihedral.sr3._inverse = Dihedral.sr3
