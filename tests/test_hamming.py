import numpy as np
import pytest

from src.gf2 import gf2_mul
from src.hamming import G, H, build_syndrome_table, correct, encode, syndrome

__all__ = ()


class TestHammingMatrices:
    """Тестирование свойств порождающей и проверочной матриц."""

    def test_shapes(self) -> None:
        """Проверить размеры матриц G и H."""
        assert G.shape == (4, 7)
        assert H.shape == (3, 7)

    def test_binary_elements(self) -> None:
        """Проверить, что матрицы содержат только бинарные элементы."""
        assert set(G.flatten().tolist()).issubset({0, 1})
        assert set(H.flatten().tolist()).issubset({0, 1})

    def test_orthogonality(self) -> None:
        """Проверить ортогональность H @ G^T = 0 mod 2."""
        product = gf2_mul(G, H.T)
        expected = np.zeros((4, 3), dtype=np.int8)
        assert np.array_equal(product, expected)

    def test_systematic_form(self) -> None:
        """Проверить систематический вид матрицы G."""
        identity = np.eye(4, dtype=np.int8)
        assert np.array_equal(G[:, :4], identity)


class TestSyndromeTable:
    """Тестирование таблицы синдромов."""

    def test_table_entries(self) -> None:
        """Проверить размер и содержание таблицы синдромов."""
        table = build_syndrome_table()
        assert len(table) == 8

        # Нулевой синдром соответствует отсутствию ошибки (-1)
        zero_key = (0, 0, 0)
        assert zero_key in table
        assert table[zero_key] == -1

        # Позиции от 0 до 6 должны присутствовать в значениях
        positions = set(table.values())
        assert positions == set(range(-1, 7))


class TestEncode:
    """Тестирование кодирования сообщений."""

    def test_encode_zero(self) -> None:
        """Проверить кодирование нулевого сообщения."""
        m = np.zeros(4, dtype=np.int8)
        c = encode(m)
        assert np.all(c == 0)
        assert len(c) == 7

    def test_encode_dimensions(self) -> None:
        """Проверить корректность размерностей при кодировании."""
        m = np.array([1, 0, 1, 0], dtype=np.int8)
        c = encode(m)
        assert c.ndim == 1
        assert len(c) == 7

    def test_invalid_input_raises_error(self) -> None:
        """Проверить вызов исключений при неверной длине сообщения."""
        m_short = np.array([1, 0, 1], dtype=np.int8)
        with pytest.raises(AssertionError):
            encode(m_short)


class TestSyndrome:
    """Тестирование вычисления синдрома."""

    def test_zero_syndrome_for_codewords(self) -> None:
        """Проверить, что все разрешенные кодовые слова имеют нулевой синдром."""
        for i in range(16):
            m = np.array([(i >> 3) & 1, (i >> 2) & 1, (i >> 1) & 1, i & 1], dtype=np.int8)
            c = encode(m)
            s = syndrome(c)
            assert np.all(s == 0)

    def test_invalid_input_raises_error(self) -> None:
        """Проверить вызов исключений при неверной длине кодового слова."""
        c_short = np.array([1, 0, 1, 0, 1, 1], dtype=np.int8)
        with pytest.raises(AssertionError):
            syndrome(c_short)


class TestCorrect:
    """Тестирование исправления ошибок."""

    def test_correct_no_error(self) -> None:
        """Проверить исправление кодового слова без ошибок."""
        table = build_syndrome_table()
        m = np.array([1, 1, 0, 0], dtype=np.int8)
        c = encode(m)
        corrected = correct(c, table)
        assert np.array_equal(corrected, c)

    def test_correct_single_error(self) -> None:
        """Проверить исправление одиночной ошибки на любой позиции."""
        table = build_syndrome_table()
        m = np.array([1, 0, 1, 1], dtype=np.int8)
        c_clean = encode(m)

        for pos in range(7):
            c_err = c_clean.copy()
            c_err[pos] = (c_err[pos] + 1) % 2
            corrected = correct(c_err, table)
            assert np.array_equal(corrected, c_clean)

    def test_invalid_syndrome_raises_error(self) -> None:
        """Проверить выброс исключения при неизвестном синдроме."""
        # Создаем таблицу без одной ошибки, чтобы спровоцировать
        # отсутствие синдрома в табличной базе
        zero_key = (0, 0, 0)
        table_broken: dict[tuple[int, ...], int] = {zero_key: -1}

        c = np.array([1, 0, 0, 0, 0, 0, 0], dtype=np.int8)
        with pytest.raises(ValueError, match="Неизвестный синдром"):
            correct(c, table_broken)
