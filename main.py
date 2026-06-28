print("====================================================")
print("     SANJUU SECURE ENCRYPT (SSE-U1) - CORE ENGINE   ")
print("====================================================\n")

import os
import argon2
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA256
from Crypto.Util.Padding import pad, unpad

def encrypt_sse_u1(input_filename, output_filename, password, rsa_public_key):
    """File ko read karke use custom .sseu1 package mein encrypt karta hai."""
    # 1. Raw file bytes read karna
    with open(input_filename, "rb") as f:
        raw_data = f.read()
        
    # 2. 64-byte Key material derive karna (Argon2id)
    salt = os.urandom(16)
    key_material = argon2.low_level.hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=2,
        memory_cost=65536,
        parallelism=4,
        hash_len=64,
        type=argon2.low_level.Type.ID
    )
    aes_key = key_material[:32]
    hmac_key = key_material[32:]
    
    # 3. AES-256 Encryption
    iv = os.urandom(16)
    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
    ciphertext = cipher_aes.encrypt(pad(raw_data, AES.block_size))
    
    # 4. HMAC Integrity Tag Generation
    hmac_engine = HMAC.new(hmac_key, digestmod=SHA256)
    hmac_engine.update(salt + iv + ciphertext)
    mac_tag = hmac_engine.digest()
    
    # 5. RSA Key Protection
    rsa_cipher = PKCS1_OAEP.new(rsa_public_key)
    protected_aes_key = rsa_cipher.encrypt(aes_key)
    
    # 6. Writing the Custom Packed Binary Format
    with open(output_filename, "wb") as f:
        f.write(protected_aes_key)  # 256 Bytes
        f.write(salt)               # 16 Bytes
        f.write(iv)                 # 16 Bytes
        f.write(mac_tag)            # 32 Bytes
        f.write(ciphertext)         # Variable Bytes
    print(f"✓ [ENCRYPT] File '{input_filename}' successfully packed into '{output_filename}'")


def decrypt_sse_u1(package_filename, target_filename, password, rsa_private_key):
    """Custom .sseu1 file ko unpack aur verify karke decrypt karta hai."""
    # 1. Package file se bytes unpack karna
    with open(package_filename, "rb") as f:
        read_protected_key = f.read(256)
        read_salt = f.read(16)
        read_iv = f.read(16)
        read_mac_tag = f.read(32)
        read_ciphertext = f.read()
        
    # 2. RSA Private key se AES Key unlock karna
    rsa_decipher = PKCS1_OAEP.new(rsa_private_key)
    unlocked_aes_key = rsa_decipher.decrypt(read_protected_key)
    
    # 3. Verification ke liye wapas HMAC key derive karna
    decrypt_key_material = argon2.low_level.hash_secret_raw(
        secret=password.encode(),
        salt=read_salt,
        time_cost=2,
        memory_cost=65536,
        parallelism=4,
        hash_len=64,
        type=argon2.low_level.Type.ID
    )
    verify_hmac_key = decrypt_key_material[32:]
    
    # 4. Integrity Check chalaana
    verifying_hmac = HMAC.new(verify_hmac_key, digestmod=SHA256)
    verifying_hmac.update(read_salt + read_iv + read_ciphertext)
    
    try:
        verifying_hmac.verify(read_mac_tag)
        print("🔒 [INTEGRITY] Verified! Packaged data is intact.")
        
        # 5. Final AES Decryption
        cipher_decrypt = AES.new(unlocked_aes_key, AES.MODE_CBC, read_iv)
        decrypted_raw = unpad(cipher_decrypt.decrypt(read_ciphertext), AES.block_size)
        
        # 6. Decrypted data ko target file mein write karna
        with open(target_filename, "wb") as f:
            f.write(decrypted_raw)
        print(f"✓ [DECRYPT] Recovered original file saved as '{target_filename}'")
        
    except ValueError:
        print("🚨 [CRITICAL ALERT] Integrity Verification Failed! Decryption Blocked.")


# --- PROGRAM EXECUTION (APPLICATION FLOW) ---
if __name__ == "__main__":
    # Setup files and keys
    master_password = input("Enter Master Software Password: ")
    
    print("\nInitializing asymmetric key components...")
    key_pair = RSA.generate(2048)
    
    # Execute Encryption
    encrypt_sse_u1("payload.txt", "secure_data.sseu1", master_password, key_pair.publickey())
    
    print("\n" + "-"*40 + "\nStarting Extraction Phase...\n" + "-"*40)
    
    # Execute Decryption
    decrypt_sse_u1("secure_data.sseu1", "recovered_data.txt", master_password, key_pair)
