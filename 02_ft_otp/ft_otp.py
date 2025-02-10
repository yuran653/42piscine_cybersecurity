#!./otp_venv/bin/python3.10

import base64
import click
import re
from click_option_group import optgroup,\
    RequiredMutuallyExclusiveOptionGroup
from Crypto.Cipher import AES


# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"


# The string is treated as binary data rather than a regular text string
# The string is stored as a sequence of bytes rather than Unicode characters
# Only ASCII characters are allowed in the content
ENCRYPTION_KEY = b'_the_insecure_static_32-bit_key_'


def generate_otp(path: str) -> None:
    print(f'{YELLOW}Generating TOTP code...{RESET}')


def validate_hex(key: str) -> bool:
    return len(key) == 64 and re.fullmatch(r'^[0-9a-fA-F]{64}$', key)


def generate_key(path: str) -> None:

    print(f"{YELLOW}Saving key '{path}' to 'ft_otp.key'...{RESET}")

    with open(path, 'r') as file:
        key = file.read().strip()
        if not validate_hex(key):
            print(f'{RED}Error: key must be 64 hexadecimal characters{RESET}')
            return
        
    with open('ft_otp.key', 'wb') as file:
        # Key Creation Process:
        # 1. Convert 64-char hex string to bytes (raw binary data)
        #    Example: '41424344' -> b'ABCD'
        key_bytes = bytes.fromhex(key)
        # 2. Initialize AES cipher in Counter (CTR) mode:
        #    - Uses 32-bit key for encryption
        #    - CTR mode automatically handles Initialization Vector
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CTR)
        # 3. Encrypt the key bytes using AES-CTR:
        #    - Combines key bytes with random stream using XOR
        #    - Produces encrypted binary output
        encrypted = cipher.encrypt(key_bytes)
        # 4. Encode encrypted data to Base64:
        #    - Converts binary data to ASCII-safe format
        #    - Makes it suitable for file storage
        #    Example: b'\x01\x02\x03' -> 'AQID'
        file.write(base64.b64encode(encrypted))

    print(f"{GREEN}Key was successfully saved in 'ft_otp.key'{RESET}")


@click.command()
@optgroup.group('Storage operations', cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option('-g',
                 type=click.Path(exists=True,
                                 dir_okay=False,
                                 file_okay=True),
                 help='Stores hexadecimal key in the file')
@optgroup.option('-k',
                 type=click.Path(exists=True,
                                 dir_okay=False,
                                 file_okay=True),
                 help='Generates and stores TOTP code into the file')
def ft_otp(g, k):
    if g:
        generate_key(g)
    elif k:
        generate_otp(k)


if __name__ == '__main__':
    ft_otp()
