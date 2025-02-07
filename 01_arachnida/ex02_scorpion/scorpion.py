import click


@click.command()
@click.argument('files', type=click.File('rb'), nargs=-1)
def scorpion(files):
    for file in files:
        # Process each image file
        pass


if __name__ == '__main__':
    scorpion(files)
