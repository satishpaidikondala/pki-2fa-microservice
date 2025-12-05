import requests
import json

# --- CONFIGURATION ---
# Replace these with your actual details
STUDENT_ID = "24A95A6114" 
REPO_URL = "https://github.com/satishpaidikondala/pki-2fa-microservice"
# ---------------------

API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

def main():
    try:
        # Read your public key
        with open("student_public.pem", "r") as f:
            public_key = f.read()

        payload = {
            "student_id": STUDENT_ID,
            "github_repo_url": REPO_URL,
            "public_key": public_key
        }

        print(f"Requesting seed for {STUDENT_ID}...")
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            enc_seed = data.get("encrypted_seed")
            print("\nSUCCESS! Received Encrypted Seed:")
            print("-" * 50)
            print(enc_seed)
            print("-" * 50)
            
            # Save it to a file so we can use it with curl easily
            with open("encrypted_seed.txt", "w") as f:
                f.write(enc_seed)
            print("\nSaved to 'encrypted_seed.txt'.")
        else:
            print(f"\nFailed: {response.text}")

    except FileNotFoundError:
        print("Error: Could not find 'student_public.pem'. Make sure you are in the correct folder.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()