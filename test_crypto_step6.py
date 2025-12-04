import time
from cryptography.hazmat.primitives import serialization
from app.crypto import decrypt_seed, generate_totp_code, verify_totp_code

def run_test():
    print("--- Testing App Logic (Windows Safe) ---")
    
    # 1. Load Keys and Encrypted Seed
    try:
        with open("student_private.pem", "rb") as kf:
            private_key = serialization.load_pem_private_key(kf.read(), None)
        with open("encrypted_seed.txt", "r") as sf:
            enc_seed_content = sf.read().strip()
    except FileNotFoundError:
        print("Missing keys or seed file!")
        return

    # 2. Test Decryption
    try:
        hex_seed = decrypt_seed(enc_seed_content, private_key)
        print("[OK] Decryption: Success")
    except Exception as e:
        print(f"[FAIL] Decryption Failed: {e}")
        return

    # 3. Test Generation
    try:
        code = generate_totp_code(hex_seed)
        print(f"[OK] Generation: Generated Code {code}")
    except Exception as e:
        print(f"[FAIL] Generation Failed: {e}")

    # 4. Test Verification
    try:
        is_valid = verify_totp_code(hex_seed, code)
        print(f"[OK] Verification: Current code is valid? {is_valid}")
        
        # Test Invalid Code
        is_invalid = verify_totp_code(hex_seed, "000000")
        print(f"[OK] Verification: '000000' is valid? {is_invalid} (Should be False)")
    except Exception as e:
        print(f"[FAIL] Verification Failed: {e}")

if __name__ == "__main__":
    run_test()