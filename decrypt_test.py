import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

def decrypt_seed_test():
    print("--- Step 5: Testing Decryption ---")

    # 1. Load Private Key
    try:
        with open("student_private.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
    except FileNotFoundError:
        print("Error: student_private.pem not found.")
        return

    # 2. Load Encrypted Seed
    try:
        with open("encrypted_seed.txt", "r") as seed_file:
            encrypted_b64 = seed_file.read().strip()
    except FileNotFoundError:
        print("Error: encrypted_seed.txt not found.")
        return

    # 3. Decrypt
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)

        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        decrypted_seed = decrypted_bytes.decode('utf-8')

        print("SUCCESS! Decryption worked.")
        print("--------------------------------------------------")
        print("YOUR HEX SEED IS BELOW (Copy this):")
        print(decrypted_seed)
        print("--------------------------------------------------")
        
    except Exception as e:
        print("Decryption Failed:")
        print(e)

if __name__ == "__main__":
    decrypt_seed_test()