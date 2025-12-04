import requests
import json
import sys
import os

# ================= USER CONFIGURATION =================
# TODO: Replace "YOUR_STUDENT_ID" with your actual ID (e.g., "12345678")
STUDENT_ID = "24A95A6114"  

# TODO: Replace with your EXACT GitHub URL (e.g., "https://github.com/johndoe/pki-2fa-service")
# CRITICAL: This must match the URL you submit later!
REPO_URL = "https://github.com/satishpaidikondala/pki-2fa-microservice" 
# ======================================================

API_ENDPOINT = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def request_seed():
    print(f"--- Step 4: Requesting Encrypted Seed ---")
    print(f"Student ID: {STUDENT_ID}")
    print(f"Repo URL:   {REPO_URL}")

    # 1. Read student public key
    if not os.path.exists("student_public.pem"):
        print("❌ Error: 'student_public.pem' not found. Please complete Step 2 first.")
        return

    with open("student_public.pem", "r") as f:
        public_key_content = f.read()

    # 2. Prepare the payload
    # Note: The requests library automatically escapes newlines to \n in the JSON body
    payload = {
        "student_id": STUDENT_ID,
        "github_repo_url": REPO_URL,
        "public_key": public_key_content
    }

    # 3. Send POST request
    try:
        print("Creating request...")
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=30)
        
        # Check for HTTP errors
        if response.status_code != 200:
            print(f"❌ API Error (Status {response.status_code}):")
            print(response.text)
            return

    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return

    # 4. Parse JSON response
    try:
        data = response.json()
        
        if "encrypted_seed" in data:
            encrypted_seed = data["encrypted_seed"]
            
            # 5. Save to file
            with open("encrypted_seed.txt", "w") as f:
                f.write(encrypted_seed)
                
            print("\n✅ SUCCESS: Encrypted seed received and saved to 'encrypted_seed.txt'")
            print(f"Seed length: {len(encrypted_seed)} characters")
        else:
            print("❌ Error: Response did not contain 'encrypted_seed'")
            print(data)

    except json.JSONDecodeError:
        print("❌ Error: Failed to parse JSON response")
        print(response.text)

if __name__ == "__main__":
    # Simple check to ensure user updated the config
    if STUDENT_ID == "YOUR_STUDENT_ID" or "yourusername" in REPO_URL:
        print("❌ STOP: You must open 'request_seed.py' and update STUDENT_ID and REPO_URL first!")
    else:
        request_seed()