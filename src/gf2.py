import numpy

__all__ = ["gf2_add", "gf2_mul"]


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


# TODO: Сделать расчет обратной матрицы над GF(2) (gf2_inv).
