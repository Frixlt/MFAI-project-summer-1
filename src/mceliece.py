import numpy as np

from src.gf2 import gf2_add, gf2_inv, gf2_mul
from src.hamming import G, H, build_syndrome_table, correct

__all__ = ["brute_force", "decrypt", "encrypt", "keygen"]


def keygen() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Генерация ключей для схемы Мак-Элиса.

    Returns:
        pk: открытый ключ (g_pub)
        sk: словарь приватных ключей (s_matrix, p_matrix, h_matrix, s_inv, p_inv)
    """
    # 1. Генерация случайной обратимой матрицы s размера 4x4
    while True:
        s = np.random.randint(0, 2, size=(4, 4), dtype=np.int8)
        try:
            s_inv = gf2_inv(s)
            break
        except ValueError:
            continue

    # 2. Генерация случайной перестановочной матрицы p размера 7x7
    perm = np.random.permutation(7)
    p = np.zeros((7, 7), dtype=np.int8)
    for i in range(7):
        p[i, perm[i]] = 1
    p_inv = p.T  # Обратная перестановочная матрица равна её транспонированной версии

    # 3. Вычисление публичного ключа g_pub = s * G * p (mod 2)
    tmp = gf2_mul(s, G)
    g_pub = gf2_mul(tmp, p)

    sk = {"S": s, "P": p, "H": H, "S_inv": s_inv, "P_inv": p_inv}
    return g_pub, sk


def encrypt(m: np.ndarray, pk: np.ndarray) -> np.ndarray:
    """Шифрование сообщения (4 бита) плюс добавление случайной ошибки веса 1.

    Args:
        m: вектор сообщения длины 4
        pk: публичный ключ g_pub (размера 4x7)
    """
    m = np.asarray(m, dtype=np.int8)
    pk = np.asarray(pk, dtype=np.int8)

    # Генерация ошибки e веса 1
    e = np.zeros(7, dtype=np.int8)
    err_pos = np.random.randint(0, 7)
    e[err_pos] = 1

    return gf2_add(gf2_mul(m, pk), e)


def decrypt(c: np.ndarray, sk: dict[str, np.ndarray]) -> np.ndarray:
    """Декодирование шифртекста при помощи приватных ключей.

    Args:
        c: шифртекст (вектор длины 7)
        sk: словарь приватных ключей
    """
    c = np.asarray(c, dtype=np.int8)
    p_inv = sk["P_inv"]
    h_matrix = sk["H"]
    s_inv = sk["S_inv"]

    # 1. Применить обратную перестановку
    c_prime = gf2_mul(c, p_inv)

    # 2. Вычислить синдром и исправить ошибку
    if np.array_equal(h_matrix, H):
        syndrome_table = build_syndrome_table()
        c_prime_corrected = correct(c_prime, syndrome_table)
    else:
        # Для кастомной проверочной матрицы (например, в тестах на ошибки)
        # строим таблицу синдромов вручную
        table = {}
        for i in range(h_matrix.shape[1]):
            e = np.zeros(h_matrix.shape[1], dtype=np.int8)
            e[i] = 1
            s = gf2_mul(e, h_matrix.T)
            table[tuple(s)] = i
        # Нулевой синдром
        table[tuple(np.zeros(h_matrix.shape[0], dtype=np.int8))] = -1

        s = gf2_mul(c_prime, h_matrix.T)
        pos = table.get(tuple(s))
        if pos is None:
            raise ValueError("Неверный синдром. Невозможно исправить ошибку.")
        c_prime_corrected = c_prime.copy()
        if pos != -1:
            c_prime_corrected[pos] = (c_prime_corrected[pos] + 1) % 2

    # 5. Извлечь систематическую часть сообщения m' = m * s (первые 4 бита)
    m_prime = c_prime_corrected[:4]

    # 6. Снять маскирование исходного сообщения m = m' * s_inv
    return gf2_mul(m_prime, s_inv)


def brute_force(c: np.ndarray, pk: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Атака полного перебора на шифртекст по открытому ключу.

    Args:
        c: шифртекст (вектор длины 7)
        pk: публичный ключ g_pub (размера 4x7)

    Returns:
        Кортеж (m, e), где m - исходное сообщение, e - вектор ошибки
    """
    c = np.asarray(c, dtype=np.int8)
    pk = np.asarray(pk, dtype=np.int8)

    for i in range(16):
        # Двоичное представление i в виде вектора длины 4
        m = np.array([(i >> 3) & 1, (i >> 2) & 1, (i >> 1) & 1, i & 1], dtype=np.int8)

        # Вычисляем e_cand = (c - m * pk) % 2
        e_cand = gf2_add(c, gf2_mul(m, pk))

        # Если вес Хэмминга равен 1, то мы нашли m и e
        if np.sum(e_cand) == 1:
            return m, e_cand

    raise ValueError("Сообщение не найдено. Возможно, добавлено более одной ошибки.")
