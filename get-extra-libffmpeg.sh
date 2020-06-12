#/bin/bash -e

# Simple script for get external libffmpeg from chromium-codecs
# Author: Alexander Makeenkov <amakeenk@altlinux.org>
# License: MIT

name="chromium-codecs-ffmpeg-extra"
yab_dir="/opt/yandex/browser-beta"

[ $(whoami) == "root" ] || exit 1

cd $(mktemp -d)

chromium_codecs_link=$(curl -s https://packages.ubuntu.com/xenial-updates/amd64/${name}/download | grep "de.archive.ubuntu.com" | cut -d "\"" -f2)

curl -s ${chromium_codecs_link} -o ${name}.deb

[ -f ${name}.deb ] && ar x ${name}.deb
[ -f data.tar.xz ] && tar xf data.tar.xz
[ -f ./usr/lib/chromium-browser/libffmpeg.so ] && cp ./usr/lib/chromium-browser/libffmpeg.so ${yab_dir}
