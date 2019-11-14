BINDIR ?= /usr/sbin

install:
	mkdir -p $(DESTDIR)$(BINDIR)
	install -m0755 yandex-browser-updater.py $(DESTDIR)$(BINDIR)/yandex-browser-updater
