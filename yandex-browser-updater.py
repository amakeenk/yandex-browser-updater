#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
from subprocess import Popen
from subprocess import PIPE
from tempfile import gettempdir
from tqdm import tqdm
from os import path
from os import symlink


class Updater():
    def __init__(self):
        self.repo_url = 'https://repo.yandex.ru/yandex-browser/rpm/beta/x86_64'
        self.package_dir = '/opt/yandex/browser-beta'
        self.libffmpeg_path = '{}/lib/libffmpeg.so'.format(self.package_dir)
        self.current_version = ''
        self.last_version = ''

    def do_action(self, cmd):
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        stdout, stderr = proc.communicate()
        exit_code = proc.returncode
        return [stdout, exit_code] if proc.returncode == 0 else [stderr, exit_code]

    def get_last_version_rpm_name(self):
        try:
            response = requests.get(self.repo_url)
            if response.status_code != 200:
                print(response.text)
                exit(1)
            for link in BeautifulSoup(response.text, 'lxml').findAll("a"):
                if 'yandex-browser-beta' in link.text:
                    return link.text
        except requests.exceptions.RequestException as err:
            print('Some error occured: {}.'.format(err.strerror))
            exit(1)

    def get_full_path_to_rpm(self):
        rpm_name = self.get_last_version_rpm_name()
        return '{}/{}'.format(self.repo_url, rpm_name)

    def get_last_version(self):
        cmd = 'rpm --query --package --queryformat="%{VERSION}" ' + self.get_full_path_to_rpm()
        return self.do_action(cmd)[0]

    def get_current_version(self):
        cmd = 'rpm --query --queryformat="%{VERSION}" yandex-browser-beta'
        return self.do_action(cmd)[0]

    def compare_versions(self):
        return 1 if self.last_version != self.current_version else 0

    def check_install(self):
        cmd = 'rpm -q yandex-browser-beta'
        if self.do_action(cmd)[1] != 0:
            print('Yandex Browser is not installed.')
            return 0
        else:
            return 1

    def download_rpm_package(self):
        print('Downloading ...')
        url = self.get_full_path_to_rpm()
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
        else:
            return output_file

    def install(self, rpm_file):
        print('Installing ...')
        cmd = 'apt-get install -y {}'.format(rpm_file)
        result = self.do_action(cmd)
        if result[1] != 0:
            print(result[0])
            exit(1)
        else:
            self.current_version = self.get_current_version()
            if self.compare_versions():
                print('New version is not installed.')
                exit(1)
            else:
                print('New version successfully installed.')

    def link_libffmpeg(self):
        symlink_path = 'libffmpeg.so'.format(self.package_dir)
        if path.isfile(self.libffmpeg_path) and not path.isfile(symlink_path):
            symlink(self.libffmpeg_path, symlink_path)

    def run(self):
        if self.check_install():
            self.current_version = self.get_current_version()
            print('Current version: {}'.format(self.current_version))
            print('Checking last version ...')
            self.last_version = self.get_last_version()
            print('Last version: {}'.format(self.last_version))
            if self.compare_versions():
                print('New version is available.')
                rpm_file = self.download_rpm_package()
                self.install(rpm_file)
            else:
                print('The latest version is already installed.')
                exit(0)
        else:
            rpm_file = self.download_rpm_package()
            self.install(rpm_file)
        self.link_libffmpeg()


def main():
    updater = Updater()
    updater.run()


if __name__ == '__main__':
    main()
