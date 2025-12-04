import os
import time
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization

# Import the logic we created in Step 6
from app.crypto import decrypt_seed, generate_totp_code, verify_totp_code

app = FastAPI()

# --- CONFIGURATION ---
# The task requires storing the seed at /data/seed.txt
# We check if /data exists (Docker), otherwise use a local 'data' folder (Windows/Testing)
if os.path.exists("/data"):
    DATA_DIR = "/data"
else:
    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)

SEED_FILE = os.path.join(DATA_DIR, "seed.txt")
PRIVATE_KEY_FILE = "student_private.pem"

# --- REQUEST MODELS ---
class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# --- ENDPOINT 1: POST /decrypt-seed ---
@app.post("/decrypt-seed", status_code=200)
def api_decrypt_seed(payload: DecryptRequest, response: Response):
    try:
        # Checklist 1: Load student private key from file
        if not os.path.exists(PRIVATE_KEY_FILE):
            # Fallback for Docker if key is in root
            key_path = f"/app/{PRIVATE_KEY_FILE}" if os.path.exists(f"/app/{PRIVATE_KEY_FILE}") else PRIVATE_KEY_FILE
        else:
            key_path = PRIVATE_KEY_FILE
            
        try:
            with open(key_path, "rb") as kf:
                private_key = serialization.load_pem_private_key(kf.read(), password=None)
        except FileNotFoundError:
            # If key is missing, we can't decrypt
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": "Private key not found"}

        # Checklist 2 & 3: Base64 decode and Decrypt using RSA/OAEP
        # (Handled inside our crypto.decrypt_seed function)
        hex_seed = decrypt_seed(payload.encrypted_seed, private_key)

        # Checklist 4: Validate decrypted seed is 64-character hex
        if len(hex_seed) != 64:
            raise ValueError("Invalid seed length")
        
        # Checklist 5: Save to /data/seed.txt
        with open(SEED_FILE, "w") as f:
            f.write(hex_seed)

        # Checklist 6: Return {"status": "ok"}
        return {"status": "ok"}

    except Exception as e:
        # Requirement: Response (500 Internal Server Error): {"error": "Decryption failed"}
        print(f"Decryption error: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Decryption failed"}


# --- ENDPOINT 2: GET /generate-2fa ---
@app.get("/generate-2fa")
def api_generate_2fa(response: Response):
    try:
        # Checklist 1: Check if /data/seed.txt exists
        if not os.path.exists(SEED_FILE):
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": "Seed not decrypted yet"}

        # Checklist 2: Read hex seed from file
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        # Checklist 3: Generate TOTP code
        code = generate_totp_code(hex_seed)

        # Checklist 4: Calculate remaining seconds (0-29)
        # Period is 30s. Time remaining = 30 - (current_time % 30)
        valid_for = 30 - (int(time.time()) % 30)

        # Checklist 5: Return code and valid_for
        return {"code": code, "valid_for": valid_for}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}


# --- ENDPOINT 3: POST /verify-2fa ---
@app.post("/verify-2fa")
def api_verify_2fa(payload: VerifyRequest, response: Response):
    try:
        # Checklist 1: Validate code is provided (Handled by Pydantic model)
        if not payload.code:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Missing code"}

        # Checklist 2: Check if /data/seed.txt exists
        if not os.path.exists(SEED_FILE):
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": "Seed not decrypted yet"}

        # Checklist 3: Read hex seed from file
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        # Checklist 4: Verify TOTP code with ±1 period tolerance
        is_valid = verify_totp_code(hex_seed, payload.code, valid_window=1)

        # Checklist 5: Return {"valid": true/false}
        return {"valid": is_valid}

    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Internal processing error"}