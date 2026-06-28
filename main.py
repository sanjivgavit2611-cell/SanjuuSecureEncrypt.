print("=== Sanjuu Secure Encrypt (SSE-U1) - Final Package ===")

import os
import argon2
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA256
from Crypto.Util.Padding import pad, unpad

# 1. User Inputs aur Dummy File creation
password_input = input("Set Master Password for SSE-U1: ")
input_file = "payload.txt"
output_package = "secure_data.sseu1"

# Ek original file bana lete hain test karne ke liye
with open(input_file, "w") as f:
    f.write("CONFIDENTIAL: This data is packed inside the custom SSE-U1 format.")

print(f"\n[1] Reading original file: {input_file}")
with open(input_file, "rb") as f:
    raw_data = f.read()

# 2. RSA Key Generation (For Session Key Protection)
print("[2] Generating RSA-2048 Cryptographic Key Pair...")
rsa_keys = RSA.generate(2048)
public_key = rsa_keys.publickey()

# 3. Key Derivation Framework (Argon2id)
print("[3] Churning password through Argon2id KDF...")
salt = os.urandom(16)
key_material = argon2.low_level.hash_secret_raw(
    secret=password_input.encode(),
    salt=salt,
    time_cost=2,
    memory_cost=65536,
    parallelism=4,
    hash_len=64,  # 32 Bytes for AES, 32 Bytes for HMAC
    type=argon2.low_level.Type.ID
)
aes_session_key = key_material[:32]
hmac_key = key_material[32:]

# 4. AES Encryption
print("[4] Encrypting data block with AES-256-CBC...")
iv = os.urandom(16)
cipher_aes = AES.new(aes_session_key, AES.MODE_CBC, iv)
ciphertext = cipher_aes.encrypt(pad(raw_data, AES.block_size))

# 5. HMAC Integrity Signature
print("[5] Generating HMAC-SHA256 signature seal...")
hmac_engine = HMAC.new(hmac_key, digestmod=SHA256)
hmac_engine.update(salt + iv + ciphertext)
mac_tag = hmac_engine.digest()

# 6. RSA Key Encapsulation (Protecting the AES Key)
print("[6] Locking AES Session Key with RSA Public Key...")
rsa_cipher = PKCS1_OAEP.new(public_key)
protected_aes_key = rsa_cipher.encrypt(aes_session_key) # Length: Always 256 bytes

# 7. Packaging into final .sseu1 file
print(f"[7] Writing integrated package to: {output_package}")
with open(output_package, "wb") as f:
    f.write(protected_aes_key)  # 256 bytes
    f.write(salt)               # 16 bytes
    f.write(iv)                 # 16 bytes
    f.write(mac_tag)            # 32 bytes
    f.write(ciphertext)         # Variable bytes

print("✓ Packaging Complete! SSE-U1 file is now armed.")

print("\n" + "="*40 + "\n--- [START DECRYPTION & UNPACKING] ---\n" + "="*40)

# 8. Unpacking the .sseu1 file
print(f"[1] Opening package: {output_package} for unpacking...")
with open(output_package, "rb") as f:
    read_protected_key = f.read(256) # Shuru ke 256 bytes alag kiye
    read_salt = f.read(16)           # Next 16 bytes
    read_iv = f.read(16)             # Next 16 bytes
    read_mac_tag = f.read(32)        # Next 32 bytes
    read_ciphertext = f.read()       # Bacha hua poora ciphertext

# 9. RSA Unlock
print("[2] Unlocking AES key using RSA Private Key...")
rsa_decipher = PKCS1_OAEP.new(rsa_keys) # Using Private Key
unlocked_aes_key = rsa_decipher.decrypt(read_protected_key)

# 10. Re-deriving HMAC Key to verify integrity
print("[3] Re-generating verification keys from password...")
decrypt_key_material = argon2.low_level.hash_secret_raw(
    secret=password_input.encode(),
    salt=read_salt,
    time_cost=2,
    memory_cost=65536,
    parallelism=4,
    hash_len=64,
    type=argon2.low_level.Type.ID
)
verify_hmac_key = decrypt_key_material[32:]

# 11. HMAC Integrity Verification
print("[4] Running Integrity Verification Check...")
verifying_hmac = HMAC.new(verify_hmac_key, digestmod=SHA256)
verifying_hmac.update(read_salt + read_iv + read_ciphertext)

try:
    verifying_hmac.verify(read_mac_tag)
    print("🔒 SUCCESS: Integrity Verified! Package has not been modified.")
    
    # 12. Final AES Decryption
    print("[5] Executing final AES Decryption...")
    cipher_decrypt = AES.new(unlocked_aes_key, AES.MODE_CBC, read_iv)
    decrypted_raw = unpad(cipher_decrypt.decrypt(read_ciphertext), AES.block_size)
    
    print(f"\n[FINAL DECRYPTED OUTPUT]: {decrypted_raw.decode()}")

except ValueError:
    print("🚨 CRITICAL ERROR: Integrity Check Failed! Data has been tampered with.")
