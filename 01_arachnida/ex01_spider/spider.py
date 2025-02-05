import click
import requests
from pathlib import Path
from bs4 import BeautifulSoup



def normalize_url(img_url: str, page_url: str) -> str:

    query_idx = img_url.find('?')
    if query_idx != -1:
        img_url = img_url[:query_idx]

    img_url = img_url.lstrip('/')

    if not img_url.startswith('https://'):
        print(img_url)
        print(img_url[:img_url.find('/')].rfind('.'))
        if img_url.startswith(page_url[8:-1]):
            img_url = 'https://' + img_url
        # elif img_url[:img_url.find('/')].
        else:
            img_url = page_url + img_url

    return img_url


def save_image(url: str, path: Path) -> None:
    # print(url)
    try:
        img_response = requests.get(url)
        img_response.raise_for_status()
        img_path = path/Path(img_response.url).name
        with open(img_path, 'wb') as file:
            file.write(img_response.content)
        print(f'\033[32mDownloaded:\33[0m {url} -> {img_path}')
    except Exception as e:
        print(f'\033[31mSave image error occurred:\033[0m {e}')
        return
    pass


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
        print('Error: Path cannot be empty')
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
            print('The script does not work with insecure connections')
            return
    except requests.exceptions.RequestException as e:
        print(e)
        return

    try:
        soup = BeautifulSoup(page_response.content, 'html.parser')
        img_tags = soup.find_all('img', src=True)
        img_urls = [img['src'] for img in img_tags]
    except (AttributeError, KeyError, TypeError) as e:
        print(e)
        return
    
    # print(*img_urls, sep='\n\n')
    
    for img_url in img_urls:
        if img_url.startswith('data:image') == False:
            save_image(normalize_url(img_url, page_response.url), dir)


if __name__ == '__main__':
    spider()
