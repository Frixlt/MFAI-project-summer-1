import numpy

__all__ = ["gf2_add", "gf2_inv", "gf2_mul"]


def gf2_add(a: numpy.ndarray, b: numpy.ndarray) -> numpy.ndarray:
    """
    Сложить два вектора или матрицы над GF(2).
    """
    a = numpy.asarray(a, dtype=numpy.int8)
    b = numpy.asarray(b, dtype=numpy.int8)
    return (a + b) % 2


def gf2_mul(a: numpy.ndarray, b: numpy.ndarray) -> numpy.ndarray:
    """
    Перемножить две матрицы (или матрицу и вектор) над GF(2).
    """
    a = numpy.asarray(a, dtype=numpy.int8)
    b = numpy.asarray(b, dtype=numpy.int8)
    return numpy.mod(a @ b, 2)


def gf2_inv(matrix: numpy.ndarray) -> numpy.ndarray:
    """
    Вычислить обратную матрицу над GF(2) методом Гаусса-Жордана.
    Возвращает матрицу или выбрасывает ValueError, если матрица вырождена.
    """
    a = numpy.asarray(matrix, dtype=numpy.int8) % 2
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError("Матрица должна быть двумерной и квадратной.")
    n = a.shape[0]
    identity = numpy.eye(n, dtype=numpy.int8)
    aug = numpy.block([a, identity])
    for i in range(n):
        pivot_row = i
        while pivot_row < n and aug[pivot_row, i] == 0:
            pivot_row += 1
        if pivot_row == n:
            raise ValueError("Матрица вырождена (необратима).")
        if pivot_row != i:
            aug[[i, pivot_row]] = aug[[pivot_row, i]]
        for j in range(n):
            if j != i and aug[j, i] == 1:
                aug[j] = aug[j] ^ aug[i]
    return aug[:, n:]
