def encrypt_railfence(text, key):
    rail = [""] * key
    row = 0
    direction = 1  

    for char in text:
        rail[row] += char
        row += direction

        if row == key - 1:
            direction = -1
        elif row == 0:
            direction = 1

    steps = "\n".join([f"Rail {i+1}: {rail[i]}" for i in range(key)])
    return "".join(rail), steps


def decrypt_railfence(cipher, key):
    rail_len = [0] * key
    row = 0
    direction = 1

    for _ in cipher:
        rail_len[row] += 1
        row += direction

        if row == key - 1:
            direction = -1
        elif row == 0:
            direction = 1

    rails = []
    index = 0
    for l in rail_len:
        rails.append(cipher[index:index + l])
        index += l

    result = ""
    pointers = [0] * key
    row = 0
    direction = 1

    for _ in cipher:
        result += rails[row][pointers[row]]
        pointers[row] += 1
        row += direction

        if row == key - 1:
            direction = -1
        elif row == 0:
            direction = 1

    return result, "Decryption visualization coming soon"
