from cryptography.fernet import Fernet

# Use the key you generated above
KEY = b'rV_M1Cjf3OBV-REO7Nrr5YZTSoqAZRATt_HtOBM1-yk='  # Replace this with your valid key
cipher_suite = Fernet(KEY)

def encrypt_message(message):
    """Encrypt the message."""
    encrypted_message = cipher_suite.encrypt(message.encode())
    return encrypted_message.decode()

def decrypt_message(encrypted_message):
    """Decrypt the message."""
    try:
        decrypted_message = cipher_suite.decrypt(encrypted_message.encode()).decode()
        return decrypted_message
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
