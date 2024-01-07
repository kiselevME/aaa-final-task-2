import pytest
from main import bots_move, won


@pytest.mark.parametrize(
    'input, expected_result',
    [
        ([['.', '.', '.'],
          ['.', '.', '.'],
          ['.', '.', '.']],
         [(0, 0), (0, 1), (0, 2),
          (1, 0), (1, 1), (1, 2),
          (2, 0), (2, 1), (2, 2)]),
        ([['X', '.', '.'],
          ['.', '.', '.'],
          ['.', '.', '.']],
         [(0, 1), (0, 2),
          (1, 0), (1, 1), (1, 2),
          (2, 0), (2, 1), (2, 2)]),
        ([['X', 'O', '.'],
          ['.', '.', 'X'],
          ['.', '.', '.']],
         [(0, 2),
          (1, 0), (1, 1),
          (2, 0), (2, 1), (2, 2)]),
        ([['X', 'O', 'O'],
          ['X', '.', 'X'],
          ['O', 'X', '.']],
         [
          (1, 1),
          (2, 2)]),
        ([['X', 'O', 'X'],
          ['X', 'O', 'O'],
          ['O', 'X', 'X']],
         [])
    ]
)
def test_bots_move(input, expected_result):
    if len(expected_result) > 0:
        # проверяем, что результат лежит среди ожидаемых результатов
        assert bots_move(input) in expected_result
    else:
        # проверяем, что возвращается ошибка
        with pytest.raises(ValueError):
            bots_move(input)


@pytest.mark.parametrize(
    'input, expected_result',
    [
        ([['.', '.', '.'],
          ['.', '.', '.'],
          ['.', '.', '.']],
         False),
        ([['X', '.', '.'],
          ['.', '.', '.'],
          ['.', '.', '.']],
         False),
        ([['X', 'O', '.'],
          ['.', '.', 'X'],
          ['.', '.', '.']],
         False),
        ([['X', 'O', 'O'],
          ['X', '.', 'O'],
          ['X', 'X', '.']],
         True),
        ([['O', 'O', 'O'],
          ['X', 'X', 'O'],
          ['X', 'X', '.']],
         True),
        ([['O', 'O', 'X'],
          ['X', 'X', 'O'],
          ['X', 'X', '.']],
         True),
        ([['O', 'O', 'X'],
          ['X', 'O', '.'],
          ['X', 'X', 'O']],
         True),
        ([['O', 'X', 'X'],
          ['X', 'O', 'O'],
          ['O', 'X', 'X']],
         False)
    ]
)
def test_won(input, expected_result):
    assert won(input) == expected_result
