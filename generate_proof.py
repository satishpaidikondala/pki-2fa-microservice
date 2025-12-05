import sys
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def main():
    print("--- Generating Commit Proof ---")

    # 1. Get Commit Hash from Command Line Argument
    if len(sys.argv) < 2:
        print("Error: You must provide the commit hash as an argument.")
        print("Usage: python generate_proof.py <COMMIT_HASH>")
        return
    
    commit_hash = sys.argv[1].strip()
    print(f"Using Commit Hash: {commit_hash}")

    # 2. Load Keys
    try:
        with open("student_private.pem", "rb") as f:
            student_priv = serialization.load_pem_private_key(f.read(), password=None)
        
        with open("instructor_public.pem", "rb") as f:
            instructor_pub = serialization.load_pem_public_key(f.read())
    except FileNotFoundError:
        print("Error: Keys (student_private.pem or instructor_public.pem) not found.")
        return

    # 3. Sign the Commit Hash (RSA-PSS)
    message = commit_hash.encode('utf-8')
    
    signature = student_priv.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # 4. Encrypt the Signature (RSA-OAEP)
    encrypted_sig = instructor_pub.encrypt(
        signature,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 5. Output Base64 (Single Line)
    final_proof = base64.b64encode(encrypted_sig).decode('utf-8')

    print("\nSUCCESS! Encrypted Commit Signature:")
    print("-" * 60)
    print(final_proof)
    print("-" * 60)

if __name__ == "__main__":
    main()