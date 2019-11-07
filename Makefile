BINDIR ?= /usr/sbin

install:
	install -m0755 yandex-browser-updater.py $(BINDIR)/yandex-browser-updater
