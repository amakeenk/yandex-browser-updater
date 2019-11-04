#!/usr/bin/python3

import requests
from argparse import ArgumentParser
from subprocess import Popen
from subprocess import PIPE
from bs4 import BeautifulSoup

repo_url = 'https://repo.yandex.ru/yandex-browser/rpm/beta/x86_64'


def args_parser():
    args = ArgumentParser()
    args.add_argument('-i', '--install', default=False, action='store_true', dest='install', help='install yandex browser')
    args_list = args.parse_args()
    return [args_list.install]


def do_action(cmd):
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    stdout, stderr = proc.communicate()
    return stdout if not stderr else stderr


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
    cmd = 'rpm --query --package --queryformat="%{VERSION}" ' + format(get_full_path_to_rpm())
    return do_action(cmd)


def get_local_version():
    cmd = 'rpm --query --queryformat="%{VERSION}" yandex-browser-beta'
    return do_action(cmd)


def main():
    print('Current version: {}'.format(get_local_version()))
    print('Check last version ...')
    print('Last available version: {}'.format(get_last_version()))


if __name__ == '__main__':
    main()
