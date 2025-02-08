import click
from PIL import Image
from PIL.ExifTags import TAGS

# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[0m"


@click.command()
@click.argument('files', type=click.File('rb'), nargs=-1)
def scorpion(files):

    file_exts=('.jpg', '.jpeg', '.png', '.gif', '.bmp')

    for buffer_reader in files:
        if buffer_reader.name.endswith(file_exts):

            with Image.open(buffer_reader) as img_obj:
                exif_data = img_obj.getexif()

            if not exif_data:
                print(f'{YELLOW}No EXIF data found in:{RESET} {buffer_reader.name}')
                buffer_reader.close()
                continue

            print(f'{GREEN}File: {buffer_reader.name}{RESET}')
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                print(f"{tag:25}: {value}")

            buffer_reader.close()
        else:
            print(f'{YELLOW}Skipping non-supporting file:{RESET} {buffer_reader.name}')
            buffer_reader.close()
            continue


if __name__ == '__main__':
    scorpion()
