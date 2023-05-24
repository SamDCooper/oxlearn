from oxlearn.training.dihedral import Dihedral

import oxlearn.board as ob


def test_associativity():
    counter = 0
    for p in Dihedral:
        for q in Dihedral:
            for r in Dihedral:
                assert (p * q) * r == p * (q * r)
                counter += 1
    assert counter == 8**3


def test_identity():
    e = Dihedral.e
    counter = 0
    for p in Dihedral:
        assert e * p == p
        assert p * e == p
        counter += 1
    assert counter == 8


def test_inverse():
    e = Dihedral.e
    counter = 0
    for p in Dihedral:
        q = ~p
        assert q * p == e
        assert p * q == e
        counter += 1
    counter == 8


def test_group_law():
    e = Dihedral.e
    r = Dihedral.r
    r2 = Dihedral.r2
    r3 = Dihedral.r3
    s = Dihedral.s
    sr = Dihedral.sr
    sr2 = Dihedral.sr2
    sr3 = Dihedral.sr3

    group_table = [
        # e r  r2  r3  s  sr  sr2  sr3
        [e, r, r2, r3, s, sr, sr2, sr3],  # e
        [r, r2, r3, e, sr3, s, sr, sr2],  # r
        [r2, r3, e, r, sr2, sr3, s, sr],  # r2
        [r3, e, r, r2, sr, sr2, sr3, s],  # r3
        [s, sr, sr2, sr3, e, r, r2, r3],  # s
        [sr, sr2, sr3, s, r3, e, r, r2],  # sr
        [sr2, sr3, s, sr, r2, r3, e, r],  # sr2
        [sr3, s, sr, sr2, r, r2, r3, e],  # sr3
    ]
    counter = 0
    i = 0
    for p in Dihedral:
        j = 0
        for q in Dihedral:
            assert p * q == group_table[i][j]
            j += 1
            counter += 1
        i += 1
    assert counter == 8**2


def test_board_action():
    # 11364 | 716   | 6028  | 16740 | 5300  | 724   | 17916 | 10908
    # . X X | X O O | O X . | . . . | X X . | O O X | . X O | . . .
    # . X O | X X X | O X . | X X X | O X . | X X X | . X O | X X X
    # . X O | . . . | X X . | O O X | O X . | . . . | . X X | X O O

    expected_results = {
        Dihedral.e: ob.Board(11364),
        Dihedral.r: ob.Board(716),
        Dihedral.r2: ob.Board(6028),
        Dihedral.r3: ob.Board(16740),
        Dihedral.s: ob.Board(5300),
        Dihedral.sr: ob.Board(724),
        Dihedral.sr2: ob.Board(17916),
        Dihedral.sr3: ob.Board(10908),
    }

    counter = 0
    untransformed_board = ob.Board(11364)
    for trans, board in expected_results.items():
        assert trans * untransformed_board == board
        counter += 1
    assert counter == 8

    counter = 0
    for a in Dihedral:
        for b in Dihedral:
            for board in expected_results.values():
                assert (a * b) * board == a * (b * board)
                counter += 1
    assert counter == 8 * 8 * 8
