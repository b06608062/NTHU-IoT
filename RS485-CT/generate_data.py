import random

length_of_string = 12500  # bytes

binary_string = "".join(random.choice("01") for _ in range(length_of_string))
print(f"{len(binary_string)} bytes")  # '0' or '1 -> 1 byte
print(f"{len(binary_string) * 8} bits")  # UTF-8 '0' or '1' -> 8 bits
file_path = "./100kbits.txt"

with open(file_path, "w") as file:
    file.write(binary_string)
