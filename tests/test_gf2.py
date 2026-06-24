import numpy
import pytest

import src.gf2

__all__ = ()


class TestGf2Add:
    "Тесты сложения над GF(2)"

    def test_add_0_plus_0(self) -> None:
        """0 + 0 = 0 для одномерных синглтонов."""
        assert numpy.array_equal(
            src.gf2.gf2_add(numpy.array([0]), numpy.array([0])), numpy.array([0])
        )

    def test_add_0_plus_1(self) -> None:
        """0 + 1 = 1 для одномерных синглтонов."""
        assert numpy.array_equal(
            src.gf2.gf2_add(numpy.array([0]), numpy.array([1])), numpy.array([1])
        )

    def test_add_1_plus_0(self) -> None:
        """1 + 0 = 1 для одномерных синглтонов."""
        assert numpy.array_equal(
            src.gf2.gf2_add(numpy.array([1]), numpy.array([0])), numpy.array([1])
        )

    def test_add_1_plus_1(self) -> None:
        """1 + 1 = 0 для одномерных синглтонов."""
        assert numpy.array_equal(
            src.gf2.gf2_add(numpy.array([1]), numpy.array([1])), numpy.array([0])
        )

    def test_add_empty_arrays(self) -> None:
        """Сложение пустых массивов"""
        a = numpy.array([], dtype=numpy.int8)
        result = src.gf2.gf2_add(a, a)
        assert result.size == 0

    def test_add_large_vector(self) -> None:
        """Сложение очень длинных векторов"""
        size = 100_000
        a = numpy.ones(size, dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_add(a, a), numpy.zeros(size, dtype=numpy.int8))

    def test_add_3d_tensors(self) -> None:
        """Сложение трехмерных тензоров"""
        a = numpy.array([[[1, 0], [0, 1]], [[1, 1], [0, 0]]], dtype=numpy.int8)
        b = numpy.array([[[0, 1], [0, 1]], [[1, 0], [1, 1]]], dtype=numpy.int8)
        expected = numpy.array([[[1, 1], [0, 0]], [[0, 1], [1, 1]]], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_add(a, b), expected)

    def test_add_different_dtypes(self) -> None:
        """Обработка разных целочисленных типов (int32, uint8, int64)."""
        a = numpy.array([1, 0], dtype=numpy.int32)
        b = numpy.array([1, 1], dtype=numpy.uint8)
        expected = numpy.array([0, 1], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_add(a, b), expected)

    def test_add_huge_even_odd_numbers(self) -> None:
        """Приведение гигантских четных/нечетных чисел по модулю 2."""
        a = numpy.array([1000000000002, 1000000000003])  # -> 0, 1
        b = numpy.array([0, 0])
        expected = numpy.array([0, 1], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_add(a, b), expected)

    def test_add_deep_negative_numbers(self) -> None:
        """Отрицательные числа"""
        a = numpy.array([-1, -2, -3], dtype=numpy.int64)
        b = numpy.array([0, 0, 0], dtype=numpy.int64)
        expected = numpy.array([1, 0, 1], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_add(a, b), expected)

    def test_add_dimension_mismatch_raises_error(self) -> None:
        """Матрица 2x2 и матрица 2x3 не могут быть сложены."""
        a = numpy.ones((2, 2))
        b = numpy.ones((2, 3))
        with pytest.raises(ValueError):
            src.gf2.gf2_add(a, b)


class TestGf2Mul:
    "Тесты умножения над GF(2)"

    def test_mul_ones_even_dimension(self) -> None:
        """Умножение матриц из одних единиц ЧЕТНОГО размера дает НУЛЕВУЮ матрицу (1+1=0)."""
        a = numpy.ones((2, 2), dtype=numpy.int8)
        expected = numpy.zeros((2, 2), dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_mul(a, a), expected)

    def test_mul_ones_odd_dimension(self) -> None:
        """Умножение матриц из одних единиц НЕЧЕТНОГО размера дает матрицу из ЕДИНИЦ (1+1+1=1)."""
        a = numpy.ones((3, 3), dtype=numpy.int8)
        expected = numpy.ones((3, 3), dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_mul(a, a), expected)

    def test_mul_rectangular_matrices(self) -> None:
        """Умножение неквадратных матриц: (2 x 3) * (3 x 4) = (2 x 4)."""
        a = numpy.array([[1, 0, 1], [0, 1, 1]], dtype=numpy.int8)
        b = numpy.array([[1, 1, 0, 0], [0, 1, 1, 0], [1, 0, 1, 1]], dtype=numpy.int8)
        expected = numpy.array([[0, 1, 1, 1], [1, 1, 0, 1]], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_mul(a, b), expected)

    def test_mul_row_by_column(self) -> None:
        """
        Умножение вектора-строки на вектор-столбец (скалярное произведение):
        (1 x 3) * (3 x 1) = (1 x 1).
        """
        a = numpy.array([[1, 1, 1]], dtype=numpy.int8)
        b = numpy.array([[1], [1], [1]], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_mul(a, b), numpy.array([[1]], dtype=numpy.int8))

    def test_mul_column_by_row(self) -> None:
        """
        Умножение вектора-столбца на вектор-строку (внешнее произведение):
        (3 x 1) * (1 x 3) = (3 x 3).
        """
        a = numpy.array([[1], [0], [1]], dtype=numpy.int8)
        b = numpy.array([[1, 1, 0]], dtype=numpy.int8)
        expected = numpy.array([[1, 1, 0], [0, 0, 0], [1, 1, 0]], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_mul(a, b), expected)

    def test_mul_nilpotent_matrix(self) -> None:
        """Умножение нильпотентной матрицы самой на себя должно давать 0."""
        a = numpy.array([[0, 1], [0, 0]], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_mul(a, a), numpy.zeros((2, 2), dtype=numpy.int8))

    def test_mul_idempotent_matrix(self) -> None:
        """Идемпотентная матрица при умножении на себя не изменяется (A * A = A)."""
        a = numpy.array([[1, 0], [1, 0]], dtype=numpy.int8)
        assert numpy.array_equal(src.gf2.gf2_mul(a, a), a)

    def test_mul_huge_numbers(self) -> None:
        """
        Промежуточное сложение при умножении больших чисел не вызывает
        overflow типа данных.
        """
        a = numpy.array([[1000000000001, 1000000000001]], dtype=numpy.int64)  # -> 1, 1
        b = numpy.array([[1000000000001], [1000000000001]], dtype=numpy.int64)  # -> 1, 1
        assert numpy.array_equal(src.gf2.gf2_mul(a, b), numpy.array([[0]], dtype=numpy.int8))

    def test_mul_negative_elements(self) -> None:
        """Корректность перемножения и модульного сокращения отрицательных значений."""
        a = numpy.array([[-1, -1]], dtype=numpy.int64)  # <=> [1, 1]
        b = numpy.array([[-1], [0]], dtype=numpy.int64)  # <=> [1, 0]
        assert numpy.array_equal(src.gf2.gf2_mul(a, b), numpy.array([[1]], dtype=numpy.int8))

    def test_mul_invalid_dimensions_raises_error(self) -> None:
        """Ошибка, если внутренние размерности матриц не совпадают: (2 x 3) и (2 x 3)."""
        a = numpy.ones((2, 3))
        b = numpy.ones((2, 3))
        with pytest.raises(ValueError):
            src.gf2.gf2_mul(a, b)
