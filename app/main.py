import os
import base64
import time
import json
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import pyotp

app = FastAPI()

# Paths configured in your Dockerfile
PRIVATE_KEY_PATH = "/app/student_private.pem"
SEED_FILE_PATH = "/data/seed.txt"

class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

def get_totp_object(hex_seed: str):
    # Requirement: Convert Hex to Base32 before generating TOTP
    try:
        # 1. Convert Hex -> Bytes
        seed_bytes = bytes.fromhex(hex_seed.strip())
        # 2. Convert Bytes -> Base32
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        # 3. Create TOTP object (Default is SHA1, 30s, 6 digits)
        return pyotp.TOTP(base32_seed)
    except Exception as e:
        raise ValueError(f"Invalid seed format: {str(e)}")

@app.post("/decrypt-seed")
def decrypt_seed(payload: DecryptRequest):
    try:
        # 1. Load Private Key
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

        # 2. Decode Base64 input
        encrypted_bytes = base64.b64decode(payload.encrypted_seed)

        # 3. Decrypt using RSA-OAEP with SHA-256 (Task requirement)
        decrypted_data = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # 4. Decode to Hex String and Validate
        hex_seed = decrypted_data.decode('utf-8').strip()
        
        if len(hex_seed) != 64:
             # Basic check to ensure it looks like a hex string
            raise ValueError("Decrypted seed is not 64 characters length")

        # 5. Save to persistent storage
        with open(SEED_FILE_PATH, "w") as f:
            f.write(hex_seed)

        return {"status": "ok"}

    except Exception as e:
        # Task requires returning HTTP 500 on failure
        print(f"Decryption error: {e}")
        raise HTTPException(status_code=500, detail="Decryption failed")

@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    try:
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        totp = get_totp_object(hex_seed)
        current_code = totp.now()
        
        # Calculate remaining validity
        valid_for = 30 - (int(time.time()) % 30)
        
        return {"code": current_code, "valid_for": valid_for}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-2fa")
def verify_2fa(payload: VerifyRequest):
    if not os.path.exists(SEED_FILE_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")
    
    try:
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()
            
        totp = get_totp_object(hex_seed)
        
        # Verify with window=1 (Task requirement: +/- 30 seconds)
        is_valid = totp.verify(payload.code, valid_window=1)
        
        return {"valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))