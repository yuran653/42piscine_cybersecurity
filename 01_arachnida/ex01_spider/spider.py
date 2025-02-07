import click
import requests
import base64
import datetime
import binascii
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque


def save_to_file(path: Path, content: bytes, saved_imgs: set) -> bool:

    img_hash = get_img_hash(content)

    if img_hash in saved_imgs or Path(path).exists():
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

    extension = absolute_url[absolute_url.rfind('.'):].lower()
    if extension not in file_exts:
        print(f"\033[33mWARNING: Extension '{extension[1:]}' is not supported\033[0m")
        return None
    
    return absolute_url
    

def get_img_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def save_img(img_url: str,
               page_url: str,
               path: Path,
               saved_imgs: set,
               file_exts=('.jpg', '.jpeg', '.png', '.gif', '.bmp')
               ) -> None:
    
    normalized_url = normalize_url(img_url, page_url, file_exts)
    if normalized_url == None:
        return
    
    try:
        img_response = requests.get(normalized_url, verify=True)
        img_response.raise_for_status()
        img_path = path/Path(img_response.url).name

        if save_to_file(img_path, img_response.content, saved_imgs):
            print(f'\033[32mDownloaded:\33[0m {normalized_url} -> {img_path}')

    except requests.exceptions.RequestException as e:
        print(f'\033[31mERROR: Save image error occurred:\033[0m {e}')
        return


def save_base64_img(img_base64: str,
                      path: Path,
                      saved_imgs: set,
                      file_types = ('jpg', 'jpeg', 'png', 'gif', 'bmp')
                      ) -> None:
    
    file_type = img_base64[img_base64.find("/"):img_base64.find(";")]

    if  file_type[1:].lower() in file_types:
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H:%M:%S.%f")
        img_path = path / f'{timestamp_str}.{file_type[1:]}'

        try:
            img_base64 = img_base64.split(',', 1)[1]
            img_data = base64.b64decode(img_base64)
        
            if save_to_file(img_path, img_data, saved_imgs):
                print(f'\033[32mDownloaded:\33[0m decoded base64 to image-> {img_path}')

        except (binascii.Error, IndexError) as e:  
            print(f"\033[31mERROR: Base64 decode failed: {e}\033[0m")  
            return  
        
    else:
        print(f"\033[33mWARNING: Extension '{file_type[1:]}' is not supported\033[0m")


def fetch_imgs(page_response: requests.Response, dir: Path, saved_imgs: set) -> None:

    try:
        soup = BeautifulSoup(page_response.content, 'html.parser')
        img_tags = soup.find_all('img', src=True)
        img_urls = {img['src'] for img in img_tags}
    except (AttributeError, KeyError, TypeError) as e:
        print(e)
        return
    
    if img_urls:
        for img_url in img_urls:
            print(f'\033[36mAttempt to download image at:\033[0m {img_url}')
            if img_url.startswith('data:image') and ';base64' in img_url:
                save_base64_img(img_url, dir, saved_imgs)
            else:
                save_img(img_url, page_response.url, dir, saved_imgs)


def fetch_urls(page_response: requests.Response, base_url: str) -> set:
    try:
        soup = BeautifulSoup(page_response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        urls = {urljoin(base_url, link['href']) for link in links}
        return {url for url in urls if url.startswith(base_url)}
    except (AttributeError, KeyError, TypeError) as e:
        print(e)
        return set()


def fetch_page(url: str) -> requests.Response:
    try:
        page_response = requests.get(url, verify=True)
        page_response.raise_for_status()
        if page_response.url.startswith('http://'):
            print('\033[33mWARNING: The script does not work with insecure connections\033[0m')
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    return page_response


@click.command()
@click.option('-r', '--recursive', is_flag=True , default=False,
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
    
    if depth < 1:
        print('\033[33mWARNING: Depth cannot be less than 1\033[0m')  
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
    
    page_response = fetch_page(url)
    if page_response is None:
        return
    
    visited = {page_response.url}
    saved_imgs = set()
    if recursive:
        urls = deque([(url, 1)])
        while urls:
            current_url, current_depth = urls.popleft()
            if current_depth >= depth:
                continue
                
            page_response = fetch_page(current_url)
            if page_response is None:
                continue

            fetch_imgs(page_response, dir, saved_imgs)

            fetched_urls = fetch_urls(page_response, url)
            for fetched_url in fetched_urls:
                if fetched_url not in visited:
                    visited.add(fetched_url)
                    urls.append((fetched_url, current_depth + 1))

    else:
        fetch_imgs(page_response, dir, saved_imgs)


if __name__ == '__main__':
    spider()
