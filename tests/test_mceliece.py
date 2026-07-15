import numpy as np
import pytest

from src.gf2 import gf2_mul
from src.hamming import H
from src.mceliece import brute_force, decrypt, encrypt, keygen

__all__ = ()


class TestKeyGen:
    """Тестирование генерации ключей схемы Мак-Элиса."""

    def test_keygen_output_structure(self) -> None:
        """Проверить типы и размеры выходных данных keygen."""
        pk, sk = keygen()
        assert pk.shape == (4, 7)
        assert isinstance(sk, dict)
        assert "S" in sk
        assert "P" in sk
        assert "H" in sk
        assert "S_inv" in sk
        assert "P_inv" in sk

    def test_permutation_matrix_properties(self) -> None:
        """Проверить свойства перестановочной матрицы p."""
        _, sk = keygen()
        p = sk["P"]
        p_inv = sk["P_inv"]

        #   Сумма по строкам и столбцам должна быть равна 1
        assert np.all(p.sum(axis=0) == 1)
        assert np.all(p.sum(axis=1) == 1)

        #   произведение P на P_inv дает единичную матрицу
        identity = np.eye(7, dtype=np.int8)
        assert np.array_equal(gf2_mul(p, p_inv), identity)


class TestEncryptDecrypt:
    """Тестирование шифрования и расшифрования."""

    def test_end_to_end_single_message(self) -> None:
        """Проверить шифрование и расшифрование одиночного сообщения."""
        pk, sk = keygen()
        m = np.array([1, 0, 1, 1], dtype=np.int8)
        c = encrypt(m, pk)
        assert c.shape == (7,)
        m_dec = decrypt(c, sk)
        assert np.array_equal(m_dec, m)

    def test_all_16_messages(self) -> None:
        """Проверить шифрование и расшифрование всех 16 возможных сообщений."""
        pk, sk = keygen()
        for i in range(16):
            m = np.array([(i >> 3) & 1, (i >> 2) & 1, (i >> 1) & 1, i & 1], dtype=np.int8)
            c = encrypt(m, pk)
            m_dec = decrypt(c, sk)
            assert np.array_equal(m_dec, m)

    def test_decrypt_custom_h_corrects_error(self) -> None:
        """Проверить декодирование, используя кастомную проверочную матрицу H."""
        pk, sk = keygen()
        m = np.array([1, 1, 0, 0], dtype=np.int8)

        # Ошибка веса 1
        c = encrypt(m, pk)
        sk_custom = sk.copy()
        sk_custom["H"] = H[[1, 0, 2], :]
        m_dec = decrypt(c, sk_custom)
        assert np.array_equal(m_dec, m)

        # Ошибка веса 0 (нет ошибок)
        c_clean = gf2_mul(m, pk)
        m_dec_clean = decrypt(c_clean, sk_custom)
        assert np.array_equal(m_dec_clean, m)

    def test_decrypt_invalid_syndrome(self) -> None:
        """Проверить вызов ошибки ValueError при некорректном sk."""
        _, sk = keygen()
        c_test = np.array([1, 0, 0, 0, 0, 0, 0], dtype=np.int8)

        # Подменяем проверочную матрицу и P_inv так, чтобы получить неверный синдром
        sk_broken = sk.copy()
        sk_broken["H"] = np.array(
            [
                [1, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0],
            ],
            dtype=np.int8,
        )
        p_inv_broken = np.zeros((7, 7), dtype=np.int8)
        p_inv_broken[0, 0] = 1
        p_inv_broken[0, 1] = 1
        sk_broken["P_inv"] = p_inv_broken

        with pytest.raises(ValueError, match="Неверный синдром"):
            decrypt(c_test, sk_broken)


class TestBruteForce:
    """Тестирование атаки полного перебора."""

    def test_brute_force_recovery(self) -> None:
        """Проверить успешность brute-force восстановления сообщения."""
        pk, _ = keygen()
        m = np.array([1, 1, 0, 1], dtype=np.int8)
        c = encrypt(m, pk)

        m_recovered, e_recovered = brute_force(c, pk)
        assert np.array_equal(m_recovered, m)
        assert np.sum(e_recovered) == 1

    def test_brute_force_no_error_raises_error(self) -> None:
        """Проверить, что brute-force падает, если нет ошибок (вектор ошибки равен 0)."""
        pk, _ = keygen()
        m = np.array([0, 1, 0, 1], dtype=np.int8)
        c_clean = gf2_mul(m, pk)

        with pytest.raises(ValueError, match="Сообщение не найдено"):
            brute_force(c_clean, pk)
