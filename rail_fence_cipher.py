"""
Rail Fence Cipher implementation (encrypt/decrypt) in pure Python.

- Keeps spaces/punctuation exactly as provided. This is cleaner for most use
  cases because the output still mirrors the original spacing; callers can strip
  spaces themselves if desired.
- Validates that `key` is an int > 1; otherwise raises ValueError.
"""


def _validate_key(key):
    if not isinstance(key, int):
        raise ValueError("Key must be an integer.")
    if key <= 1:
        raise ValueError("Key must be greater than 1.")


def rail_fence_encrypt(plaintext, key):
    """
    Encrypts plaintext using the Rail Fence (zigzag) cipher.

    The text is written diagonally on `key` rails, top to bottom then bottom to
    top repeatedly. Reading the rails row by row produces the ciphertext.
    Spaces and punctuation are preserved exactly as given.
    """
    _validate_key(key)
    if not plaintext:
        return ""

    # Initialize rails as list of strings (one per rail).
    rails = [""] * key

    # Direction toggles when we hit the top or bottom rail.
    row = 0
    direction = 1  # 1 = moving downwards, -1 = moving upwards

    for ch in plaintext:
        rails[row] += ch
        # Flip direction at the boundaries (top or bottom rail).
        if row == 0:
            direction = 1
        elif row == key - 1:
            direction = -1
        row += direction

    # Concatenate rows to form the ciphertext.
    return "".join(rails)


def rail_fence_decrypt(ciphertext, key):
    """
    Decrypts ciphertext produced by the Rail Fence cipher.

    The algorithm reconstructs the zigzag pattern positions, marks where
    characters would go, fills them in rail by rail, then reads them off in
    zigzag order.
    """
    _validate_key(key)
    if not ciphertext:
        return ""

    length = len(ciphertext)

    # Step 1: Mark positions visited during zigzag traversal.
    # We build a matrix of placeholders to identify the zigzag path.
    pattern = [["" for _ in range(length)] for _ in range(key)]
    row = 0
    direction = 1
    for col in range(length):
        pattern[row][col] = "*"  # placeholder mark
        if row == 0:
            direction = 1
        elif row == key - 1:
            direction = -1
        row += direction

    # Step 2: Fill the placeholders row by row with ciphertext characters.
    idx = 0
    for r in range(key):
        for c in range(length):
            if pattern[r][c] == "*":
                pattern[r][c] = ciphertext[idx]
                idx += 1

    # Step 3: Read characters following the zigzag to rebuild plaintext.
    result = []
    row = 0
    direction = 1
    for col in range(length):
        result.append(pattern[row][col])
        if row == 0:
            direction = 1
        elif row == key - 1:
            direction = -1
        row += direction

    return "".join(result)


if __name__ == "__main__":
    # Small example demonstrating both encryption and decryption.
    sample_text = "Rail Fence Cipher Example"
    sample_key = 3

    encrypted = rail_fence_encrypt(sample_text, sample_key)
    decrypted = rail_fence_decrypt(encrypted, sample_key)

    print(f"Plaintext : {sample_text}")
    print(f"Key       : {sample_key}")
    print(f"Encrypted : {encrypted}")
    print(f"Decrypted : {decrypted}")

