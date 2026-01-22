# standard
import os
import stat
import tempfile
from hashlib import sha512
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import join
from subprocess import CalledProcessError
from subprocess import run

# 3rd-party
import toml
import requests


HERE = dirname(__file__)
SHASUM_FILENAME = 'SHASUM512'

meta = {}
with open(join(HERE, 'pyproject.toml'), 'r') as data:
    meta = toml.loads(data.read())

VERSION = (
    meta.get('project', {}).get('version')
    or meta.get('tool', {}).get('poetry', {}).get('version')
)
if not VERSION:
    raise RuntimeError('version not found in pyproject.toml')


log = lambda m: print(' ~ ' + m)

def download_and_write(filename):
    dest_path = abspath(join(HERE, 'vrelease', 'bin', filename))
    url = 'https://github.com/vrelease/vrelease/releases/download/v{}/{}'.format(VERSION, filename)

    req = requests.get(url, stream=True, timeout=30)
    req.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, dir=dirname(dest_path)) as tmp_file:
        for chunk in req.iter_content(chunk_size=8192):
            if chunk:
                tmp_file.write(chunk)
        tmp_path = tmp_file.name
    os.replace(tmp_path, dest_path)

    return dest_path


def get_sha512_hex_of(filepath):
    digest = sha512()
    with open(filepath, 'rb') as data:
        for chunk in iter(lambda: data.read(8192), b''):
            digest.update(chunk)
    return digest.hexdigest()


def make_executable(filepath):
    mode = os.stat(filepath).st_mode
    os.chmod(filepath, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main():
    log('downloading artifacts')
    files = [
        download_and_write('vrelease-' + f)
        for f in [
            'linux',
            'linux-arm64',
            'macos-arm64',
            'macos-x86_64',
            'windows.exe',
        ]
    ]

    log('calculating hashes')
    shasum = []
    for file in files:
        make_executable(file)
        shasum.append('{} {}'.format(get_sha512_hex_of(file), basename(file)))

    with open(join(HERE, SHASUM_FILENAME), 'w') as file:
        file.write('\n'.join(shasum))

    try:
        log('closing tag')
        run(['git', 'add', SHASUM_FILENAME], check=True)
        run(['git', 'commit', '-m', 'chore: update binary hashes'], check=True)
        run(['git', 'tag', 'v' + VERSION], check=True)
    except CalledProcessError as err:
        log('got: ' + str(err))
        log('skipping tag...')

    log('done')


if __name__ == '__main__':
    main()
