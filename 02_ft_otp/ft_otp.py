#!./otp_venv/bin/python3.10


import click
from click_option_group import optgroup,\
    RequiredMutuallyExclusiveOptionGroup

@click.command()
@optgroup.group('Storage operations', cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option('-g',
                 type=click.Path(exists=False,
                                 dir_okay=False,
                                 file_okay=True),
                 help='Store hexadecimal key')
@optgroup.option('-k',
                 type=click.Path(exists=True,
                                 dir_okay=False,
                                 file_okay=True),
                 help='Generate TOTP code')
def ft_otp(g, k):
    if g:
        print(f'Storing key: {g}')
    elif k:
        print(f'Generating TOTP code: {k}')


if __name__ == '__main__':
    ft_otp()
