print("--- Sanjuu Secure Encrypt (SSE-U1) - Phase 7 ---")

import os
import argon2
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA256
from Crypto.Util.Padding import pad, unpad

# 1. Base Setup (Inputs)
password_input = input("Enter encryption password: ")
message = b"Top Secret Data inside Phase 7 Hybrid System"

print("\n[RSA SETUP] Generating 2048-bit RSA Key Pair (Public & Private)...")
# 2. RSA Public aur Private Key generate karna
rsa_key_pair = RSA.generate(2048)
private_key = rsa_key_pair
public_key = rsa_key_pair.publickey()

print("Success! RSA Keys generated.")

print("\n[AES SETUP] Deriving AES & HMAC keys from password...")
salt = os.urandom(16)
key_material = argon2.low_level.hash_secret_raw(
    secret=password_input.encode(),
    salt=salt,
    time_cost=2,
    memory_cost=65536,
    parallelism=4,
    hash_len=64,
    type=argon2.low_level.Type.ID
)
aes_key = key_material[:32]
hmac_key = key_material[32:]

print("\n--- [STEP A: ENCRYPT DATA WITH AES] ---")
iv = os.urandom(16)
cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
ciphertext = cipher_aes.encrypt(pad(message, AES.block_size))
print(f"Data Encrypted with AES. Ciphertext (Hex): {ciphertext[:10].hex()}...")

print("\n--- [STEP B: PROTECT AES KEY WITH RSA] ---")
# 3. RSA Cipher Engine banana Public Key ka use karke
rsa_cipher_encrypt = PKCS1_OAEP.new(public_key)

# 4. AES Key ko RSA se Encrypt (Protect) karna
protected_aes_key = rsa_cipher_encrypt.encrypt(aes_key)
print(f"AES Key is now protected by RSA! Protected Key (Hex): {protected_aes_key[:10].hex()}...")


print("\n--- [STEP C: UNLOCK AES KEY WITH RSA PRIVATE KEY] ---")
# 5. Decryption ke liye RSA Private Key ka cipher engine banana
rsa_cipher_decrypt = PKCS1_OAEP.new(private_key)

# 6. Protected key ko wapas normal AES key mein decrypt karna
unlocked_aes_key = rsa_cipher_decrypt.decrypt(protected_aes_key)

# 7. Verify karna ki kya purani key aur nayi key same hain
if unlocked_aes_key == aes_key:
    print("🔒 RSA UNLOCK SUCCESS: Exact AES Session Key recovered!")
    
    # 8. Recovered Key se data decrypt karna
    cipher_decrypt = AES.new(unlocked_aes_key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher_decrypt.decrypt(ciphertext), AES.block_size)
    print(f"Decrypted Data: {decrypted_data.decode()}")
