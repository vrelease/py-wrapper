# standard
from os import system
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import join
from hashlib import sha512

# 3rd-party
import toml
import requests


HERE = dirname(__file__)
SHASUM_FILENAME = 'SHASUM512'

meta = {}
with open(join(HERE, 'pyproject.toml'), 'r') as data:
    meta = toml.loads(data.read())

VERSION = meta['tool']['poetry']['version']


log = lambda m: print(' ~ ' + m)

def download_and_write(filename):
    dest_path = abspath(join(HERE, 'vrelease', 'bin', filename))
    url = 'https://github.com/vrelease/vrelease/releases/download/v{}/{}'.format(VERSION, filename)

    req = requests.get(url, stream=True)
    with open(dest_path, 'wb') as file:
        for chunk in req.iter_content(chunk_size=8192):
            file.write(chunk)

    return dest_path


def get_sha512_hex_of(filepath):
    with open(filepath, 'rb') as data:
        return sha512(data.read()).hexdigest()


def main():
    log('downloading artifacts')
    files = [download_and_write('vrelease-' + f) for f in ['linux', 'macos', 'windows.exe']]

    log('calculating hashes')
    shasum = []
    for file in files:
        system('chmod +x ' + file)
        shasum.append('{} {}'.format(get_sha512_hex_of(file), basename(file)))

    with open(join(HERE, SHASUM_FILENAME), 'w') as file:
        file.write('\n'.join(shasum))

    try:
        log('closing tag')
        system('git add ' + SHASUM_FILENAME)
        system('git commit -m "chore: update binary hashes"')
        system('git tag v' + VERSION)
    except Exception as err:
        log('got: ' + str(err))
        log('skipping tag...')

    log('done')


if __name__ == '__main__':
    main()
