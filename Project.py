from pqcrypto.kem.ml_kem_768 import (
    generate_keypair,
    encrypt,
    decrypt
)

#Генерация ключей
public_key, secret_key = generate_keypair()

#Шифрование и расшифровка
ciphertext, shared_secret_alice = encrypt(public_key)
shared_secret_bob = decrypt(secret_key, ciphertext)

print(shared_secret_alice == shared_secret_bob)


from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

#Преобразование общего секрета в ключ AES с использованием HKDF
aes_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'ML-KEM AES key'
).derive(shared_secret_alice)

print(aes_key)
