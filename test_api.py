import requests
import json
import time
import sys

BASE_URL = "http://localhost:8080"

def run_tests():
    print("--- STARTING FINAL SYSTEM TEST (Windows Safe) ---")

    # 1. Read the encrypted seed from your local file
    try:
        with open("encrypted_seed.txt", "r") as f:
            encrypted_seed = f.read().strip()
    except FileNotFoundError:
        print("[FAIL] Error: encrypted_seed.txt not found!")
        return

    # TEST 1: Decrypt Seed
    print("\n1. Testing /decrypt-seed...")
    try:
        payload = {"encrypted_seed": encrypted_seed}
        resp = requests.post(f"{BASE_URL}/decrypt-seed", json=payload)
        if resp.status_code == 200:
            print("   [OK] Success! Seed decrypted and stored.")
        else:
            print(f"   [FAIL] Failed: {resp.text}")
            return
    except requests.exceptions.ConnectionError:
        print("   [FAIL] Error: Could not connect to localhost:8080. Is Docker running?")
        print("   Run: docker-compose up -d")
        return

    # TEST 2: Generate 2FA
    print("\n2. Testing /generate-2fa...")
    resp = requests.get(f"{BASE_URL}/generate-2fa")
    if resp.status_code == 200:
        data = resp.json()
        code = data.get("code")
        print(f"   [OK] Success! Generated Code: {code}")
        print(f"   [INFO] Valid for: {data.get('valid_for')} seconds")
    else:
        print(f"   [FAIL] Failed: {resp.text}")
        return

    # TEST 3: Verify 2FA
    print("\n3. Testing /verify-2fa...")
    verify_payload = {"code": code}
    resp = requests.post(f"{BASE_URL}/verify-2fa", json=verify_payload)
    if resp.status_code == 200 and resp.json().get("valid") is True:
        print("   [OK] Success! The code was verified as VALID.")
    else:
        print(f"   [FAIL] Failed: {resp.text}")

    print("\n--- Waiting 70 seconds to check Cron Job (Do not close)... ---")
    time.sleep(70)
    
    print("\n4. Checking Cron Logs:")
    print("   Run this command in your terminal now to see the logs:")
    print("   docker exec pki_2fa_service cat /cron/last_code.txt")

if __name__ == "__main__":
    run_tests()