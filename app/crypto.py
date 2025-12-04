import base64
import pyotp
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Step 5: Decrypt base64-encoded encrypted seed using RSA/OAEP
    """
    try:
        # 1. Base64 decode
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)

        # 2. RSA/OAEP decrypt
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 3. Decode to UTF-8 string and Return
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        raise e

def generate_totp_code(hex_seed: str) -> str:
    """
    Step 6: Generate current TOTP code from hex seed
    """
    # 1. Convert hex seed to bytes
    seed_bytes = bytes.fromhex(hex_seed)
    
    # 2. Convert bytes to base32 encoding (Required for TOTP)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    # 3. Create TOTP object (SHA-1, 30s period, 6 digits are default)
    totp = pyotp.TOTP(base32_seed)
    
    # 4. Generate current TOTP code
    return totp.now()

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Step 6: Verify TOTP code with time window tolerance
    valid_window=1 means accept codes from ±30 seconds (1 period)
    """
    # 1. Convert hex seed to base32
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    # 2. Create TOTP object
    totp = pyotp.TOTP(base32_seed)
    
    # 3. Verify with tolerance
    # valid_window=1 checks: [Current-30s, Current, Current+30s]
    return totp.verify(code, valid_window=valid_window)