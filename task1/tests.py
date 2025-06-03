import pytest
from solution import sum_two, sum_three


def test_sum_two_correct_types():
    assert sum_two(1, 2) == 3
    assert sum_two(0, 0) == 0


def test_sum_two_incorrect_type_first_arg():
    with pytest.raises(TypeError):
        sum_two(1.5, 2)


def test_sum_two_incorrect_type_second_arg():
    with pytest.raises(TypeError):
        sum_two(1, "2")


def test_sum_two_incorrect_both_args():
    with pytest.raises(TypeError):
        sum_two(1.5, "2")


def test_sum_three_correct_types():
    result = sum_three(1, 3.2, True)
    assert result == 1 + 3.2 + True

    result = sum_three(a=2, b=2.3, c=False)
    assert result == 2 + 2.3 + False


def test_sum_three_incorrect_type_a():
    with pytest.raises(TypeError):
        sum_three(1.5, 3.2, True)


def test_sum_three_incorrect_type_b():
    with pytest.raises(TypeError):
        sum_three(1, "3.2", True)


def test_sum_three_incorrect_type_c():
    with pytest.raises(TypeError):
        sum_three(1, 3.2, c="False")


def test_sum_three_incorrect_all():
    with pytest.raises(TypeError):
        sum_three("1", "3.2", "False")