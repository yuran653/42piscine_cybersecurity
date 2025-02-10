#!./otp_venv/bin/python3.10

import base64
import click
import re
import time
import hmac
import struct
from oathtool import generate_otp
from hashlib import sha1
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


def validate_against_oathtool(hex_key: str, totp: str) -> bool:
    # Validation Process Against Reference Tool:
    # 1. Convert hex key back to bytes
    #    Example: '41424344' -> b'ABCD'
    key_bytes = bytes.fromhex(hex_key)
    # 2. Convert to Base32 format
    #    - oathtool requires Base32 encoded keys
    #    - Decode to string for command line use
    base32_key = base64.b32encode(key_bytes).decode('utf-8')
    # 3. Generate reference TOTP using oathtool
    #    - Uses same key and time window
    oathtool_totp = generate_otp(base32_key)
    # 4. Compare generated TOTP with reference
    #    - Returns True if codes match
    return totp == oathtool_totp


def generate_six_digits(truncated: int) -> str:
    # Six-Digit Code Generation:
    # 1. Apply modulo 1000000 to get 6 digits
    #    - Ensures output is always 6 digits
    #    Example: 12345678 -> 345678
    # 2. Add leading zeros if necessary
    #    - zfill(6) pads with zeros to length 6
    #    Example: 12345 -> 012345
    return str(truncated % 1000000).zfill(6)


def dynamic_truncate(hmac_result: bytes) -> int:
    # Dynamic Truncation Process (RFC 4226):
    # 1. Get offset from last byte of HMAC
    #    - Use last byte & 0xf (0-15) as index
    #    Example: if last byte is 0x23, offset = 3
    offset = hmac_result[-1] & 0xf
    # 2. Extract 4 bytes starting at offset
    #    - Take continuous sequence of 4 bytes
    #    - Creates 32-bit (4-byte) number
    four_bytes = hmac_result[offset:offset + 4]
    # 3. Convert to 31-bit unsigned integer
    #    - Convert bytes to integer (big-endian)
    #    - & 0x7fffffff masks highest bit to ensure positive
    return int.from_bytes(four_bytes, byteorder='big') & 0x7fffffff


def generate_hmac(key: bytes, counter: int) -> bytes:
    # HMAC-SHA1 Generation Process:
    # 1. Convert counter to 8-byte big-endian format
    #    - '>Q' format: > (big-endian), Q (unsigned long long)
    #    Example: 1234 -> b'\x00\x00\x00\x00\x00\x00\x04\xd2'
    counter_bytes = struct.pack('>Q', counter)
    # 2. Create HMAC using SHA1
    #    - Use decrypted key as HMAC key
    #    - Use counter bytes as message
    #    - SHA1 produces 20-byte (160-bit) hash
    hmac_obj = hmac.new(key, counter_bytes, sha1)
    # 3. Get raw bytes of HMAC result
    #    - Returns 20-byte digest for truncation
    return hmac_obj.digest()


def get_time_counter() -> int:
    # Time-Based Counter Generation:
    # 1. Define standard TOTP time step
    #    - RFC 6238 recommends 30 seconds
    time_step = 30
    # 2. Get current Unix timestamp
    #    - Number of seconds since epoch (Jan 1, 1970)
    current_time = int(time.time())
    # 3. Calculate counter value
    #    - Integer division of timestamp by time step
    #    - Creates unique value for each 30-second window
    counter = current_time // time_step
    return counter


def validate_hex(key: str) -> bool:
    return len(key) == 64 and re.fullmatch(r'^[0-9a-fA-F]{64}$', key)


def my_generate_otp(path: str) -> None:

    print(f'{YELLOW}Generating TOTP code...{RESET}')

    with open(path, 'r') as file:
        # Key Decryption Process:
        # 1. Read base64-encoded encrypted key from file
        key = file.read().strip()
        # 2. Decode base64 back to encrypted bytes
        #    Example: 'AQID' -> b'\x01\x02\x03'
        decoded = base64.b64decode(key)
        # 3. Initialize AES cipher in Counter (CTR) mode
        #    - Uses same 32-bit key as for encryption
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CTR)
        # 4. Decrypt the key bytes using AES-CTR
        #    - Reverses the encryption process
        decrypted = cipher.decrypt(decoded)
        # 5. Convert decrypted bytes to hex string
        #    - Validates the original 64-char hex format
        hex_key = decrypted.hex()
        if not validate_hex(hex_key):
            print(f'{RED}Error: key must be 64 hexadecimal characters{RESET}')
            return

        # TOTP Generation Process:
        # 1. Get time-based counter (Unix time / 30 seconds)
        counter = get_time_counter()
        # 2. Generate HMAC-SHA1 using decrypted key and counter
        hmac_result = generate_hmac(decrypted, counter)
        # 3. Perform dynamic truncation to get 31-bit integer
        truncated = dynamic_truncate(hmac_result)
        # 4. Generate 6-digit TOTP code using modulo
        totp = generate_six_digits(truncated)
        
        if validate_against_oathtool(hex_key, totp):
            print(f'{GREEN}Verified: ', end='')
        else:
            print(f'{RED}Verification failed:', end='')

        print(f'{totp}{RESET}')

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
        my_generate_otp(k)


if __name__ == '__main__':
    ft_otp()
