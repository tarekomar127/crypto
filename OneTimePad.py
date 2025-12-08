import base64
import secrets
import os
from typing import Tuple, List, Dict

def _to_bytes(s: str) -> bytes:
    """Encode string to UTF-8 bytes."""
    return s.encode('utf-8')


def _from_bytes(b: bytes) -> str:
    """Try decode UTF-8 bytes to string; if fail return hex."""
    try:
        return b.decode('utf-8')
    except Exception:
        return b.hex()

def generate_key_bytes(length: int) -> bytes:
    """Generate secure random bytes of given length."""
    return secrets.token_bytes(length)


def generate_key_b64(length: int) -> str:
    """Return a base64-encoded random key for given byte length."""
    return base64.b64encode(generate_key_bytes(length)).decode('ascii')

def encrypt_bytes(plaintext_bytes: bytes, key_bytes: bytes) -> bytes:
    """XOR plaintext bytes with key bytes."""
    if len(key_bytes) < len(plaintext_bytes):
        raise ValueError("Key must be at least as long as plaintext (in bytes) for OTP.")
    return bytes([p ^ k for p, k in zip(plaintext_bytes, key_bytes)])


def decrypt_bytes(cipher_bytes: bytes, key_bytes: bytes) -> bytes:
    """OTP decrypt is same as encrypt (XOR)."""
    return encrypt_bytes(cipher_bytes, key_bytes)


def encrypt_text(plaintext: str, key_b64: str = None, auto_key: bool = True) -> Tuple[str, str]:
    """
    Encrypt plaintext (str) and return (cipher_b64, key_b64).
    - If key_b64 is provided it is used (must be long enough).
    - If no key_b64 and auto_key True, a random key is generated with length = len(plaintext in bytes).
    """
    pbytes = _to_bytes(plaintext)
    if key_b64:
        kbytes = base64.b64decode(key_b64)
        if len(kbytes) < len(pbytes):
            raise ValueError("Provided key is too short for this plaintext.")
    else:
        if not auto_key:
            raise ValueError("No key provided and auto_key is False.")
        kbytes = generate_key_bytes(len(pbytes))
        key_b64 = base64.b64encode(kbytes).decode('ascii')

    cbytes = encrypt_bytes(pbytes, kbytes)
    cipher_b64 = base64.b64encode(cbytes).decode('ascii')
    return cipher_b64, key_b64


def decrypt_text(cipher_b64: str, key_b64: str) -> str:
    """
    Decrypt a base64 ciphertext using base64 key and return plaintext string (or hex if bytes are not valid UTF-8).
    """
    cbytes = base64.b64decode(cipher_b64)
    kbytes = base64.b64decode(key_b64)
    if len(kbytes) < len(cbytes):
        raise ValueError("Provided key is too short for this ciphertext.")
    pbytes = decrypt_bytes(cbytes, kbytes)
    return _from_bytes(pbytes)


def _is_printable_byte(b: int) -> bool:
  
    return 32 <= b <= 126


def _readable_byte(b: int) -> str:

    if _is_printable_byte(b):
        return chr(b)
    return hex(b)


def get_visualization_steps(text: str, key_b64: str, mode: str = 'encrypt') -> List[Dict]:
    """
    Produce a list of steps describing each byte transformation for visualization.
    - mode = 'encrypt': 'text' is plaintext (normal str). We show plaintext byte XOR key -> cipher byte.
    - mode = 'decrypt': 'text' is base64 ciphertext (string). We show cipher byte XOR key -> plaintext byte.
    Each step is a dict:
      {
        'index': i,
        'original_bytes': [int],
        'original_repr': str,   # readable char or hex
        'key_byte': int,
        'xor_byte': int,
        'result_repr': str,     # readable char or hex
        'note': str
      }
    """
    steps = []

    if mode == 'encrypt':
        plain_bytes = _to_bytes(text)
        kbytes = base64.b64decode(key_b64)
        if len(kbytes) < len(plain_bytes):
            raise ValueError("Key too short for visualization.")
        for i, p in enumerate(plain_bytes):
            kb = kbytes[i]
            xb = p ^ kb
            step = {
                'index': i,
                'original_bytes': [p],
                'original_repr': _readable_byte(p),
                'key_byte': kb,
                'xor_byte': xb,
                'result_repr': _readable_byte(xb),
                'note': f"{p} XOR {kb} = {xb}"
            }
            steps.append(step)

    elif mode == 'decrypt':

        cbytes = base64.b64decode(text)
        kbytes = base64.b64decode(key_b64)
        if len(kbytes) < len(cbytes):
            raise ValueError("Key too short for visualization.")
        for i, c in enumerate(cbytes):
            kb = kbytes[i]
            xb = c ^ kb
            step = {
                'index': i,
                'original_bytes': [c],
                'original_repr': _readable_byte(c),
                'key_byte': kb,
                'xor_byte': xb,
                'result_repr': _readable_byte(xb),
                'note': f"{c} XOR {kb} = {xb}"
            }
            steps.append(step)
    else:
        raise ValueError("mode must be 'encrypt' or 'decrypt'")

    return steps


def save_text_file(path: str, text: str, encoding: str = 'utf-8') -> None:
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, 'w', encoding=encoding) as f:
        f.write(text)


def load_text_file(path: str, encoding: str = 'utf-8') -> str:
    with open(path, 'r', encoding=encoding) as f:
        return f.read()


def save_binary_file(path: str, data: bytes) -> None:
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def load_binary_file(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()


if __name__ == "__main__":

    import argparse
    import json
    parser = argparse.ArgumentParser(description="OTP addon demo")
    parser.add_argument('--demo', action='store_true', help='Run quick interactive demo')
    parser.add_argument('--visual', action='store_true', help='Show visual steps as JSON in demo')
    args = parser.parse_args()

    if args.demo:
        print("OTP addon quick demo (UTF-8 aware).")
        plain = input("Plaintext: ")
        cipher_b64, key_b64 = encrypt_text(plain, key_b64=None, auto_key=True)
        print("\nCipher (base64):", cipher_b64)
        print("Key (base64):", key_b64)
        recovered = decrypt_text(cipher_b64, key_b64)
        print("\nDecrypted:", recovered)
        if args.visual:
            steps = get_visualization_steps(plain, key_b64, mode='encrypt')
            print("\nVisualization steps (JSON):")
            print(json.dumps(steps, ensure_ascii=False, indent=2))
    else:
        print("Module loaded. Use from your GUI: encrypt_text / decrypt_text / generate_key_b64 / get_visualization_steps")
