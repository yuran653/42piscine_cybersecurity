import click
from pathlib import Path
import requests
from bs4 import BeautifulSoup


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
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return
    
    # try:
    #     soup = 
    # except Exception as e:
    #     print(f'An error occurred: {e}')
    #     return


if __name__ == '__main__':
    spider()
