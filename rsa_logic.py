# rsa_logic.py (updated)
import random
import re


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = extended_gcd(b % a, a)
        return g, x - (b // a) * y, y


def mod_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        return None
    return (x % m + m) % m


def is_prime(num):
    if num is None: return False
    if not isinstance(num, int): return False
    if num < 2: return False
    if num == 2: return True
    if num % 2 == 0: return False
    for i in range(3, int(num**0.5) + 1, 2):
        if num % i == 0: return False
    return True


def complete_keys(p, q, e_input=None, d_input=None):
    if not is_prime(p) or not is_prime(q):
        raise ValueError("P and Q must be prime numbers.")
    if p == q:
        raise ValueError("P and Q must be distinct.")

    n = p * q
    phi = (p - 1) * (q - 1)

    e = e_input
    d = d_input

    # Case 1: Both exist
    if e is not None and d is not None:
        if (e * d) % phi != 1:
            raise ValueError(f"User keys mismatch: (e={e}, d={d}) are not inverse.")
        if gcd(e, phi) != 1:
            raise ValueError(f"e ({e}) is not coprime with phi.")

    # Case 2: Only e exists
    elif e is not None:
        if gcd(e, phi) != 1:
            raise ValueError(f"Fixed e ({e}) is invalid for these primes.")
        d = mod_inverse(e, phi)

    # Case 3: Only d exists
    elif d is not None:
        if gcd(d, phi) != 1:
            raise ValueError(f"Fixed d ({d}) is invalid for these primes.")
        e = mod_inverse(d, phi)

    # Case 4: None
    else:
        e = 65537
        if e >= phi or gcd(e, phi) != 1:
            e = 3
            while gcd(e, phi) != 1:
                e += 2
        d = mod_inverse(e, phi)

    return e, n, d


def parse_cipher_string(s):
    """
    Robust parser for ciphertext input. It extracts all integer tokens from the
    given string and returns them as a list of ints.

    Accepts forms like:
      "11,22,33"
      "11 22 33"
      "[11, 22, 33]"
      "11\n22\n33"
      "11,22  ,  33"
    """
    if s is None:
        raise ValueError("Empty cipher string")

    # Find all sequences of digits (positive integers)
    tokens = re.findall(r"\d+", s)
    if not tokens:
        raise ValueError("No integer tokens found in cipher string")

    return [int(t) for t in tokens]


def rsa_encrypt_with_steps(text, e, n):
    cipher_ints = []
    steps_log = []

    steps_log.append(f"Encryption Formula: C = (M ^ {e}) mod {n}")
    steps_log.append("-" * 30)

    for char in text:
        m = ord(char)
        if m >= n:
            raise ValueError(f"Char '{char}' (code {m}) >= n ({n}). Use larger primes or chunking.")

        c = pow(m, e, n)
        cipher_ints.append(str(c))
        steps_log.append(f"'{char}' ({m}) -> {m}^{e} % {n} = {c}")

    return ", ".join(cipher_ints), "\n".join(steps_log)


def rsa_decrypt_with_steps(cipher_str, d, n):
    """
    فك التشفير مع إظهار الخطوات. الآن يدعم صيغ مختلفة للـ cipher بفضل parse_cipher_string.
    """
    try:
        parts = parse_cipher_string(cipher_str)
        plain_chars = []
        steps_log = []

        steps_log.append(f"Decryption Formula: M = (C ^ {d}) mod {n}")
        steps_log.append("-" * 30)

        for c in parts:
            # المعادلة الرياضية
            m = pow(c, d, n)
            try:
                char_res = chr(m)
            except ValueError:
                # If m is not a valid Unicode code point, show placeholder
                char_res = '?'

            plain_chars.append(char_res)

            # تسجيل الخطوة
            step = f"Cipher ({c}) -> {c}^{d} % {n} = {m} ('{char_res}')"
            steps_log.append(step)

        return "".join(plain_chars), "\n".join(steps_log)

    except Exception as e:
        raise ValueError(f"Invalid Cipher Format or Key: {str(e)}")


# Simple helpers for file IO to be used by the GUI
def load_text_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save_text_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

