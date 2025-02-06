import click
import requests
import base64
import datetime
import binascii
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def save_to_file(path: Path, content: bytes) -> bool:

    if Path(path).exists():
        print(f'\033[33mWARNING: Image already exists:\033[0m {path}')
        return False
    
    else:
        with open(path, 'wb') as file:
            file.write(content)

    return True
            

def normalize_url(img_url: str,
                  page_url: str,
                  file_exts: tuple
                  ) -> str:

    query_idx = img_url.find('?')
    if query_idx != -1:
        img_url = img_url[:query_idx]

    absolute_url = urljoin(page_url, img_url)

    extension = absolute_url[absolute_url.rfind('.'):]
    if not absolute_url.endswith(file_exts):
        print(f"\033[33mWARNING: Extension '{extension[1:]}' is not supported\033[0m")
        return None
    
    return absolute_url


def save_image(img_url: str,
               page_url: str,
               path: Path,
               file_exts=('.jpg', '.jpeg', '.png', '.gif', '.bmp')
               ) -> None:
    
    normalized_url = normalize_url(img_url, page_url, file_exts)
    if normalized_url == None:
        return
    
    try:
        img_response = requests.get(normalized_url)
        img_response.status_code
        img_response.raise_for_status()
        img_path = path/Path(img_response.url).name

        if save_to_file(img_path, img_response.content):
            print(f'\033[32mDownloaded:\33[0m {normalized_url} -> {img_path}')

    except requests.exceptions.RequestException as e:
        print(f'\033[31mERROR: Save image error occurred:\033[0m {e}')
        return


def save_base64_image(img_base64: str,
                      path: Path,
                      file_types = ('jpg', 'jpeg', 'png', 'gif', 'bmp')
                      ) -> None:
    
    file_type = img_base64[img_base64.find("/"):img_base64.find(";")].lower()

    if  file_type[1:] in file_types:
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H:%M:%S.%f")
        img_path = path / f'{timestamp_str}.{file_type[1:]}'

        try:
            img_base64 = img_base64.split(',', 1)[1]
            img_data = base64.b64decode(img_base64)
        except (binascii.Error, IndexError) as e:  
            print(f"\033[31mERROR: Base64 decode failed: {e}\033[0m")  
            return  

        if save_to_file(img_path, img_data):
            print(f'\033[32mDownloaded:\33[0m decoded base64 to image-> {img_path}')

    else:
        print(f"\033[33mWARNING: Extension '{file_type[1:]}' is not supported\033[0m")


@click.command()
@click.option('-r', '--recursive', is_flag=True, default=False,
              help='Enables recursive crawling of links found\
              on the target webpage')
@click.option('-l', '--depth', default=5,
              help='Sets the maximum recursion depth when -r is active')
@click.option('-p', '--path', default='./data',
              help='Specifies the directory to store downloaded images')
@click.argument('url', type=str, required=True)
def spider(recursive: bool, depth: int, path: str, url: str) -> None:
    """
    URL - the mandatory argument that sets the target website to scrape
    for images
    """
    if path == '':
        print('\033[33mWARNING: Path cannot be empty\033[0m')  
        return
    
    try:
        dir = Path(path)
        dir.mkdir(parents=True, exist_ok=True)
        test_file = dir/'test.tmp'
        test_file.touch()
        test_file.unlink()
    except (FileExistsError, PermissionError,
            NotADirectoryError, OSError) as e:
        print(e)
        return
    
    try:
        page_response = requests.get(url)
        page_response.raise_for_status()
        if page_response.url.startswith('http://'):
            print('\033[33mWARNING: The script does not work with insecure connections\033[0m')
            return
    except requests.exceptions.RequestException as e:
        print(e)
        return

    try:
        soup = BeautifulSoup(page_response.content, 'html.parser')
        img_tags = soup.find_all('img', src=True)
        img_urls = {img['src'] for img in img_tags}
    except (AttributeError, KeyError, TypeError) as e:
        print(e)
        return
    

    for img_url in img_urls:
        print(f'\033[36mAttempt to download image at:\033[0m {img_url}')
        if img_url.startswith('data:image') and ';base64' in img_url:
            save_base64_image(img_url, dir)
        else:
            save_image(img_url, page_response.url, dir)
            pass


if __name__ == '__main__':
    spider()
