PREFIX ?= /usr
DESTDIR ?=

PYTHON_VERSION := $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
SITE_PACKAGES = $(DESTDIR)$(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages/omarchy_msi_rgb

.PHONY: install uninstall

install:
	# Python library modules
	install -dm755 $(SITE_PACKAGES)
	install -Dm644 lib/omarchy_msi_rgb/__init__.py $(SITE_PACKAGES)/__init__.py
	install -Dm644 lib/omarchy_msi_rgb/core.py $(SITE_PACKAGES)/core.py
	install -Dm644 lib/omarchy_msi_rgb/keymap.py $(SITE_PACKAGES)/keymap.py
	install -Dm644 lib/omarchy_msi_rgb/theme.py $(SITE_PACKAGES)/theme.py
	install -Dm644 lib/omarchy_msi_rgb/patterns.py $(SITE_PACKAGES)/patterns.py
	install -Dm644 lib/omarchy_msi_rgb/config.py $(SITE_PACKAGES)/config.py

	# Executable scripts
	install -Dm755 bin/omarchy-msi-rgb $(DESTDIR)$(PREFIX)/bin/omarchy-msi-rgb
	install -Dm755 bin/omarchy-msi-rgb-apply $(DESTDIR)$(PREFIX)/bin/omarchy-msi-rgb-apply

	# udev rules
	install -Dm644 share/udev/99-msi-steelseries.rules $(DESTDIR)/etc/udev/rules.d/99-msi-steelseries.rules

	# Sample hook
	install -Dm644 share/omarchy/hooks/theme-set.sample $(DESTDIR)$(PREFIX)/share/omarchy-msi-rgb/hooks/theme-set.sample

	# License
	install -Dm644 LICENSE $(DESTDIR)$(PREFIX)/share/licenses/omarchy-msi-rgb/LICENSE

uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages/omarchy_msi_rgb
	rm -f $(DESTDIR)$(PREFIX)/bin/omarchy-msi-rgb
	rm -f $(DESTDIR)$(PREFIX)/bin/omarchy-msi-rgb-apply
	rm -f $(DESTDIR)/etc/udev/rules.d/99-msi-steelseries.rules
	rm -rf $(DESTDIR)$(PREFIX)/share/omarchy-msi-rgb
	rm -rf $(DESTDIR)$(PREFIX)/share/licenses/omarchy-msi-rgb
