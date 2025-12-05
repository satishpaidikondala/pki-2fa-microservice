#!/usr/bin/env python3
import os
import base64
import time
import datetime
import pyotp

# Paths
SEED_FILE_PATH = "/data/seed.txt"
# Note: Output path is handled by the redirect in the cron file (>>), 
# but printing to stdout is required.

def main():
    # 1. Check if seed exists
    if not os.path.exists(SEED_FILE_PATH):
        print(f"Error: Seed file not found at {SEED_FILE_PATH}")
        return

    try:
        # 2. Read Seed
        with open(SEED_FILE_PATH, "r") as f:
            hex_seed = f.read().strip()

        # 3. Generate TOTP (Same logic as App)
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        totp = pyotp.TOTP(base32_seed)
        
        code = totp.now()

        # 4. Get UTC Timestamp
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S")

        # 5. Print formatted output
        print(f"{timestamp_str} - 2FA Code: {code}")

    except Exception as e:
        print(f"Error generating TOTP: {e}")

if __name__ == "__main__":
    main()