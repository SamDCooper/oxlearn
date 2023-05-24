import math
import pytest

import oxlearn.training.permutation as op


@pytest.fixture(name="test_size")
def fixt_test_size() -> int:
    return 4


def all_permutations(n_elements):
    # https://en.wikipedia.org/wiki/Steinhaus–Johnson–Trotter_algorithm
    if n_elements == 1:
        return [op.Permutation(0)]
    else:
        subpermutations = all_permutations(n_elements - 1)
        permutations = []

        insert_elem = n_elements - 1
        for subper in subpermutations:
            mapping_ext = subper.mapping
            if len(mapping_ext) < n_elements - 1:
                mapping_ext += tuple(range(len(mapping_ext), n_elements - 1))
            for i in range(len(mapping_ext) + 1):
                l = list(mapping_ext)
                l.insert(i, insert_elem)
                permutations.append(op.Permutation(*l))
        return permutations


@pytest.fixture(name="all_perms")
def fixt_all_perms(test_size) -> list[op.Permutation]:
    perms = all_permutations(test_size)
    assert len(perms) == math.factorial(test_size)
    return list(reversed(perms))


def test_associativity(test_size, all_perms):
    counter = 0
    for p in all_perms:
        for q in all_perms:
            for r in all_perms:
                assert (p * q) * r == p * (q * r)
                counter += 1

    assert counter == len(all_perms) ** 3


def test_identity(test_size, all_perms):
    e = op.Permutation()
    counter = 0
    for p in all_perms:
        assert e * p == p
        assert p * e == p
        counter += 1
    assert counter == len(all_perms)


def test_inverse(test_size, all_perms):
    e = op.Permutation()

    counter = 0
    for p in all_perms:
        q = ~p
        assert q * p == e
        assert p * q == e
        counter += 1
    assert counter == len(all_perms)


def test_permute_int(test_size, all_perms):
    e = op.Permutation()
    counter = 0
    for i in range(test_size):
        assert e * i == i
        counter += 1
    assert counter == test_size

    counter = 0
    for p in all_perms:
        for i in range(test_size):
            assert p * i == p.extended_mapping(test_size)[i]
            counter += 1
    assert counter == len(all_perms) * test_size


def test_action_tuple(test_size, all_perms):
    e = op.Permutation()
    counter = 0
    for r in all_perms:
        tup = r.extended_mapping(test_size)
        assert e * tup == tup
        counter += 1
    assert counter == len(all_perms)

    counter = 0
    for p in all_perms:
        for q in all_perms:
            tup = tuple(range(test_size))
            assert (
                p * (q * tup) == (p * q) * tup
            ), f"\np={repr(p)}\nq={repr(q)}\npq={repr(p*q)}"
            counter += 1
    assert counter == len(all_perms) ** 2

    counter = 0
    for p in all_perms:
        assert p * tuple(range(test_size)) == p.extended_mapping(test_size)
        counter += 1
    assert counter == len(all_perms)


def test_cycles():
    cyc = op.Permutation.cycle(0, 1, 2) * op.Permutation.cycle(3, 4, 5)
    assert cyc * 0 == 1
    assert cyc * 1 == 2
    assert cyc * 2 == 0
    assert cyc * 3 == 4
    assert cyc * 4 == 5
    assert cyc * 5 == 3
