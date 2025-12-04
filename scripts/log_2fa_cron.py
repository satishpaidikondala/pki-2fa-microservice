#!/usr/bin/env python3
import sys
import os
import datetime
import sys

# Add the /app directory to the python path so we can import app.crypto
sys.path.append('/app')

try:
    from app.crypto import generate_totp_code
except ImportError as e:
    print(f"Error importing app.crypto: {e}", file=sys.stderr)
    sys.exit(1)

# Path to the persistent seed file (mounted volume)
SEED_FILE = "/data/seed.txt"

def main():
    # 1. Read hex seed from persistent storage
    try:
        if not os.path.exists(SEED_FILE):
            print(f"Error: Seed file not found at {SEED_FILE}", file=sys.stderr)
            return

        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
            
        if not hex_seed:
            print("Error: Seed file is empty", file=sys.stderr)
            return

    except Exception as e:
        print(f"Error reading seed file: {e}", file=sys.stderr)
        return

    # 2. Generate current TOTP code
    try:
        code = generate_totp_code(hex_seed)
    except Exception as e:
        print(f"Error generating TOTP: {e}", file=sys.stderr)
        return

    # 3. Get current UTC timestamp
    # CRITICAL: Must use UTC to match server time
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    timestamp_str = now_utc.strftime("%Y-%m-%d %H:%M:%S")

    # 4. Output formatted line
    # This goes to stdout, which cron redirects to /cron/last_code.txt
    print(f"{timestamp_str} - 2FA Code: {code}")

if __name__ == "__main__":
    main()