import numpy as np

from src.gf2 import gf2_mul

__all__ = [
    "G",
    "H",
    "build_syndrome_table",
    "correct",
    "encode",
    "syndrome",
]

# Порождающая матрица G (размер 4x7) в систематическом виде: [I_4 | P]
# I_4 - единичная матрица 4x4, P - матрица чётности 4x3.
G: np.ndarray = np.array(
    [
        [1, 0, 0, 0, 1, 1, 0],
        [0, 1, 0, 0, 1, 0, 1],
        [0, 0, 1, 0, 0, 1, 1],
        [0, 0, 0, 1, 1, 1, 1],
    ],
    dtype=np.int8,
)

# Проверочная матрица H (размер 3x7) в виде: [P^T | I_3]
# P^T - транспонированная матрица чётности, I_3 - единичная матрица 3x3.
H: np.ndarray = np.array(
    [
        [1, 1, 0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 1],
    ],
    dtype=np.int8,
)


def encode(message: np.ndarray) -> np.ndarray:
    """Кодирует 4-битное сообщение в 7-битное кодовое слово.

    Принимает вектор-строку длины 4 и умножает её на порождающую матрицу G
    над полем GF(2).
    """
    message = np.asarray(message, dtype=np.int8)
    assert message.ndim == 1, "Сообщение должно быть одномерным вектором."
    assert len(message) == 4, "Сообщение должно иметь длину 4."

    msg_2d = message[np.newaxis, :]
    code_2d = gf2_mul(msg_2d, G)
    return code_2d[0]


def syndrome(codeword: np.ndarray) -> np.ndarray:
    """Вычисляет синдром для 7-битного принятого слова.

    Формула синдрома: s = (r * H^T) % 2.
    Если синдром состоит из одних нулей, ошибок в кодовом слове нет.
    """
    codeword = np.asarray(codeword, dtype=np.int8)
    assert codeword.ndim == 1, "Кодовое слово должно быть одномерным вектором."
    assert len(codeword) == 7, "Кодовое слово должно иметь длину 7."

    code_2d = codeword[np.newaxis, :]
    syn_2d = gf2_mul(code_2d, H.T)
    return syn_2d[0]


def build_syndrome_table() -> dict[tuple[int, ...], int]:
    """Строит таблицу синдромов для исправления одиночных ошибок.

    Ключ словаря — кортеж значений синдрома (например, (1, 0, 1)).
    Значение — индекс бита в кодовом слове (0-6), в котором произошла ошибка.
    Для нулевого синдрома (ошибок нет) возвращает индекс -1.
    """
    table: dict[tuple[int, ...], int] = {}

    zero_syndrome = tuple(np.zeros(3, dtype=np.int8))
    table[zero_syndrome] = -1

    for pos in range(7):
        e = np.zeros(7, dtype=np.int8)
        e[pos] = 1
        s = syndrome(e)
        table[tuple(s)] = pos

    return table


def correct(codeword: np.ndarray, syndrome_table: dict[tuple[int, ...], int]) -> np.ndarray:
    """Исправление одиночной ошибки в кодовом слове по таблице синдромов.

    Возвращает исправленное 7-битное кодовое слово.
    """
    codeword_copy = codeword.copy()
    s = syndrome(codeword_copy)
    s_tuple = tuple(s)

    if s_tuple not in syndrome_table:
        raise ValueError(f"Неизвестный синдром {list(s)} — возможно более 1 ошибки.")

    pos = syndrome_table[s_tuple]
    if pos != -1:
        codeword_copy[pos] = (codeword_copy[pos] + 1) % 2

    return codeword_copy
