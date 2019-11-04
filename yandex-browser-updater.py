#!/usr/bin/python3

import requests
from sys import argv
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from subprocess import Popen
from subprocess import PIPE
from tempfile import gettempdir
from tqdm import tqdm

repo_url = 'https://repo.yandex.ru/yandex-browser/rpm/beta/x86_64'


def args_parser():
    args = ArgumentParser()
    args.add_argument('-i', '--install', default=False, action='store_true', dest='install', help='install yandex browser')
    args_list = args.parse_args()
    return [args_list.install]


def do_action(cmd):
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = proc.communicate()
    exit_code = proc.returncode
    return [stdout, exit_code] if proc.returncode == 0 else [stderr, exit_code]


def get_last_version_rpm_name():
    try:
        response = requests.get(repo_url)
        if response.status_code != 200:
            print(response.text)
            exit(1)
        for link in BeautifulSoup(response.text, 'lxml').findAll("a"):
            if 'yandex-browser-beta' in link.text:
                return link.text
    except requests.exceptions.RequestException as err:
        print('Some error occured: {}.'.format(err.strerror))
        exit(1)


def get_full_path_to_rpm():
    rpm_name = get_last_version_rpm_name()
    return '{}/{}'.format(repo_url, rpm_name)


def get_last_version():
    cmd = 'rpm --query --package --queryformat="%{VERSION}" ' + get_full_path_to_rpm()
    return do_action(cmd)[0]


def get_current_version():
    cmd = 'rpm --query --queryformat="%{VERSION}" yandex-browser-beta'
    return do_action(cmd)[0]


def compare_versions(current_version, last_version):
    return 1 if last_version != current_version else 0


def check_install():
    cmd = 'rpm -q yandex-browser-beta'
    if do_action(cmd)[1] != 0:
        print('Yandex Browser is not installed.')
        print('For installation use {} --install'.format(argv[0]))
        exit(1)


def download_rpm_package():
    url = get_full_path_to_rpm()
    output_file = '{}/{}'.format(gettempdir(), url.split('/')[-1])
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    tqdm_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(output_file, "wb") as file:
        for data in response.iter_content(1024):
            tqdm_bar.update(len(data))
            file.write(data)
    tqdm_bar.close()
    if total_size != 0 and tqdm_bar.n != total_size:
        print("Some error occurred while download.")
        exit(1)


def main():
    check_install()
    current_version = get_current_version()
    print('Current version: {}'.format(current_version))
    print('Check last version ...')
    last_version = get_last_version()
    print('Last version: {}'.format(last_version))
    if compare_versions(current_version, last_version):
        print('New version is available.')
        print('Download rpm package ...')
        download_rpm_package()
        print('Install new version of Yandex Browser')
    else:
        print('The latest version is already installed.')
        exit(0)


if __name__ == '__main__':
    main()
