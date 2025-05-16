import hashlib
def generate_hash(password):
    return hashlib.sha256(password.encode()).hexadigest()

def create_signature(message,private_key):
    hased=generate_hash(message)
    return int(hashed, 16)^private_key

def verify_signature(message, signature, public_key):
    hashed=generate_hash(message)
    return int(hashed, 16)==signature^public_key
message="Hello Secure"
private_key=99999
public_key=99999

signature=create_signature(message,private_key)
print("Signature:",signature)
print("Verification:",verify_signature(message,signature,public_key))