import os
import argon2
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA256
from Crypto.Util.Padding import pad, unpad

PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"

def get_or_create_rsa_keys():
    """Storage se keys load ya generate karta hai."""
    if os.path.exists(PRIVATE_KEY_FILE) and os.path.exists(PUBLIC_KEY_FILE):
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = RSA.import_key(f.read())
        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key = RSA.import_key(f.read())
        return private_key, public_key
    else:
        key_pair = RSA.generate(2048)
        private_key = key_pair
        public_key = key_pair.publickey()
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(private_key.export_key())
        with open(PUBLIC_KEY_FILE, "wb") as f:
            f.write(public_key.export_key())
        return private_key, public_key

def encrypt_sse_u1(input_filename, output_filename, password, rsa_public_key):
    if not os.path.exists(input_filename):
        print(f"\n🚨 Error: '{input_filename}' file nahi mili! Pehle file banayein.")
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
        f.write(protected_aes_key)
        f.write(salt)
        f.write(iv)
        f.write(mac_tag)
        f.write(ciphertext)
    print(f"\n🔒 Success! '{input_filename}' ko encrypt karke '{output_filename}' bana diya gaya hai.")

def decrypt_sse_u1(package_filename, target_filename, password, rsa_private_key):
    if not os.path.exists(package_filename):
        print(f"\n🚨 Error: Encrypted package '{package_filename}' nahi mila!")
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
        print(f"\n🔓 Success! Integrity Verified. Decrypted file saved as '{target_filename}'")
    except ValueError:
        print("\n🚨 CRITICAL ERROR: Password galat hai ya file ke sath chhedchhad hui hai!")

# --- INTERACTIVE USER INTERFACE MENU ---
if __name__ == "__main__":
    # Pehle purani ya nayi keys ready kar lena background mein
    private_key, public_key = get_or_create_rsa_keys()
    
    while True:
        print("\n" + "="*45)
        print("     SANJUU SECURE ENCRYPT SYSTEM (SSE-U1)   ")
        print("="*45)
        print("1. Encrypt a File (Pack to .sseu1)")
        print("2. Decrypt a File (Unpack from .sseu1)")
        print("3. Exit Application")
        
        choice = input("\nSelect an option (1-3): ")
        
        if choice == "1":
            file_to_lock = input("Enter the filename to encrypt (e.g., secret.txt): ")
            master_pass = input("Set encryption password: ")
            encrypt_sse_u1(file_to_lock, "secure_data.sseu1", master_pass, public_key)
            
        elif choice == "2":
            file_to_unlock = input("Enter the .sseu1 package name (e.g., secure_data.sseu1): ")
            master_pass = input("Enter your master password: ")
            output_name = input("Enter name for recovered file (e.g., unlocked.txt): ")
            decrypt_sse_u1(file_to_unlock, output_name, master_pass, private_key)
            
        elif choice == "3":
            print("\nThank you for using SSE-U1. Stay secure! Goodbye.")
            break
            
        else:
            print("\n🚨 Invalid choice! Please type 1, 2, or 3.")
