print("====================================================")
print("     SANJUU SECURE ENCRYPT (SSE-U1) - V2 (KEY MGMT) ")
print("====================================================\n")

import os
import argon2
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA256
from Crypto.Util.Padding import pad, unpad

# Files ke naam define karna
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"

def get_or_create_rsa_keys():
    """Yeh function keys ko disk par save aur load karne ka kaam karta hai."""
    # 1. Check karna ki kya chabi pehle se bani hui storage mein maujood hai
    if os.path.exists(PRIVATE_KEY_FILE) and os.path.exists(PUBLIC_KEY_FILE):
        print("[KEY MANAGER] Found existing RSA keys on storage. Loading them...")
        
        # Purani Private Key load karna
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = RSA.import_key(f.read())
            
        # Purani Public Key load karna
        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key = RSA.import_key(f.read())
            
        return private_key, public_key
    else:
        print("[KEY MANAGER] No keys found. Generating a brand new RSA-2048 pair...")
        # Nayi chabi generate karna
        key_pair = RSA.generate(2048)
        private_key = key_pair
        public_key = key_pair.publickey()
        
        # Nayi Private Key ko hamesha ke liye save karna (.export_key() text mein badalta hai)
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(private_key.export_key())
            
        # Nayi Public Key ko save karna
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(public_key.export_key())
            
        print("✓ [KEY MANAGER] New keys generated and saved to storage permanently.")
        return private_key, public_key

def encrypt_sse_u1(input_filename, output_filename, password, rsa_public_key):
    """File ko secure .sseu1 package mein pack karna."""
    if not os.path.exists(input_filename):
        print(f"🚨 Error: Target file '{input_filename}' nahi mili!")
        return

    with open(input_filename, "rb") as f:
        raw_data = f.read()
        
    salt = os.urandom(16)
    key_material = argon2.low_level.hash_secret_raw(
        secret=password.encode(), salt=salt, time_cost=2,
        memory_cost=65536, parallelism=4, hash_len=64,
        type=argon2.low_level.Type.ID
    )
    aes_key = key_material[:32]
    hmac_key = key_material[32:]
    
    iv = os.urandom(16)
    cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
    ciphertext = cipher_aes.encrypt(pad(raw_data, AES.block_size))
    
    hmac_engine = HMAC.new(hmac_key, digestmod=SHA256)
    hmac_engine.update(salt + iv + ciphertext)
    mac_tag = hmac_engine.digest()
    
    rsa_cipher = PKCS1_OAEP.new(rsa_public_key)
    protected_aes_key = rsa_cipher.encrypt(aes_key)
    
    with open(output_filename, "wb") as f:
        f.write(protected_aes_key)  # 256 Bytes
        f.write(salt)               # 16 Bytes
        f.write(iv)                 # 16 Bytes
        f.write(mac_tag)            # 32 Bytes
        f.write(ciphertext)         # Variable Bytes
    print(f"✓ [ENCRYPT] Encrypted package saved as '{output_filename}'")


def decrypt_sse_u1(package_filename, target_filename, password, rsa_private_key):
    """Package ko decrypt karke asli file nikalna."""
    if not os.path.exists(package_filename):
        print(f"🚨 Error: Encrypted file '{package_filename}' nahi mili!")
        return

    with open(package_filename, "rb") as f:
        read_protected_key = f.read(256)
        read_salt = f.read(16)
        read_iv = f.read(16)
        read_mac_tag = f.read(32)
        read_ciphertext = f.read()
        
    rsa_decipher = PKCS1_OAEP.new(rsa_private_key)
    unlocked_aes_key = rsa_decipher.decrypt(read_protected_key)
    
    decrypt_key_material = argon2.low_level.hash_secret_raw(
        secret=password.encode(), salt=read_salt, time_cost=2,
        memory_cost=65536, parallelism=4, hash_len=64,
        type=argon2.low_level.Type.ID
    )
    verify_hmac_key = decrypt_key_material[32:]
    
    verifying_hmac = HMAC.new(verify_hmac_key, digestmod=SHA256)
    verifying_hmac.update(read_salt + read_iv + read_ciphertext)
    
    try:
        verifying_hmac.verify(read_mac_tag)
        cipher_decrypt = AES.new(unlocked_aes_key, AES.MODE_CBC, read_iv)
        decrypted_raw = unpad(cipher_decrypt.decrypt(read_ciphertext), AES.block_size)
        
        with open(target_filename, "wb") as f:
            f.write(decrypted_raw)
        print(f"🔒 [INTEGRITY] Success! Decrypted file saved as '{target_filename}'")
    except ValueError:
        print("🚨 [CRITICAL] Tampering detected or wrong password! Decryption blocked.")


if __name__ == "__main__":
    master_password = input("Enter Master Password: ")
    
    # 1. Chabi ko check, generate ya load karna
    private_key, public_key = get_or_create_rsa_keys()
    
    # Pehli baar chalane ke liye ek file bana dete hain test karne ko
    with open("payload.txt", "w") as f:
        f.write("Sanjuu's ultra-secure persisted content!")

    # Execution Flow
    encrypt_sse_u1("payload.txt", "secure_data.sseu1", master_password, public_key)
    decrypt_sse_u1("secure_data.sseu1", "recovered_data.txt", master_password, private_key)
