import oxlearn.board as ob


def test_board():
    # 11364 | 716   | 6028  | 16740 | 5300  | 724   | 17916 | 10908
    # . X X | X O O | O X . | . . . | X X . | O O X | . X O | . . .
    # . X O | X X X | O X . | X X X | O X . | X X X | . X O | X X X
    # . X O | . . . | X X . | O O X | O X . | . . . | . X X | X O O
    assert ob.Board(11364).representation == (0, 2, 2, 0, 2, 1, 0, 2, 1)
    assert ob.Board(716).representation == (2, 1, 1, 2, 2, 2, 0, 0, 0)
    assert ob.Board(6028).representation == (1, 2, 0, 1, 2, 0, 2, 2, 0)
    assert ob.Board(16740).representation == (0, 0, 0, 2, 2, 2, 1, 1, 2)
    assert ob.Board(5300).representation == (2, 2, 0, 1, 2, 0, 1, 2, 0)
    assert ob.Board(724).representation == (1, 1, 2, 2, 2, 2, 0, 0, 0)
    assert ob.Board(17916).representation == (0, 2, 1, 0, 2, 1, 0, 2, 2)
    assert ob.Board(10908).representation == (0, 0, 0, 2, 2, 2, 2, 1, 1)


def test_available_positions():
    counter = 0
    for code in ob.Board.all_board_codes():
        board = ob.Board(code)
        repre = board.representation
        available_positions = []
        if not board.game_over:
            for i in range(len(repre)):
                if repre[i] == 0:
                    available_positions.append(i)
        assert list(board.available_positions) == available_positions

        counter += 1
    assert counter != 0


def test_add_position():
    for code in ob.Board.all_board_codes():
        board = ob.Board(code)
        repre = board.representation

        num_os = sum(1 for x in repre if x == ob.BoardSymbol.O)
        num_xs = sum(1 for x in repre if x == ob.BoardSymbol.X)
        symbol_to_play = (
            ob.BoardSymbol.first if num_xs == num_os else ob.BoardSymbol.first.next
        )

        for pos in board.available_positions:
            new_board = board + pos
            new_representation = []
            for i in range(len(repre)):
                if i == pos:
                    new_representation.append(symbol_to_play)
                else:
                    new_representation.append(repre[i])
            assert list(new_board.representation) == new_representation
