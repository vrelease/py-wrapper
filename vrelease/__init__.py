# standard
import platform
import subprocess
import sys
from os.path import abspath
from os.path import dirname
from os.path import join


def get_platform_bin():
    osys = platform.system()
    arch = platform.machine()

    if osys == 'Linux':
        if arch in ('x86_64', 'AMD64'):
            return 'linux'
        if arch in ('arm64', 'aarch64'):
            return 'linux-arm64'
        raise RuntimeError('unsupported architecture ' + arch)

    if osys == 'Darwin':
        if arch in ('x86_64', 'AMD64'):
            return 'macos-x86_64'
        if arch in ('arm64',):
            return 'macos-arm64'
        raise RuntimeError('unsupported architecture ' + arch)

    if osys == 'Windows':
        return 'windows.exe'

    raise RuntimeError('unsupported platform ' + osys)


def main():
    try:
        file = 'vrelease-' + get_platform_bin()
        bin_path = abspath(join(dirname(__file__), 'bin', file))

        result = subprocess.run([bin_path, *sys.argv[1:]])
        sys.exit(result.returncode)

    except Exception as err:  # pylint: disable=broad-except
        print(str(err))
        sys.exit(2)


if __name__ == '__main__':
    main()
