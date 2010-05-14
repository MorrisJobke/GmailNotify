#!/bin/sh

mkdir -p build-deb/usr/lib/gmailnotify
cp gmailnotify.py build-deb/usr/lib/gmailnotify
chmod +x build-deb/usr/lib/gmailnotify/gmailnotify.py
cp gmailnotifykeyring.py build-deb/usr/lib/gmailnotify
cp gmailnotify-settings.py build-deb/usr/lib/gmailnotify
cp gmailnotify.desktop build-deb/usr/lib/gmailnotify
cp gmailnotify-settings.glade build-deb/usr/lib/gmailnotify		
chmod +x build-deb/usr/lib/gmailnotify/gmailnotify-settings.py
mkdir -p build-deb/usr/share/applications
cp gmailnotify-settings.desktop build-deb/usr/share/applications
mkdir -p build-deb/usr/share/pixmaps
cp gmailnotify.svg build-deb/usr/share/pixmaps
mkdir -p build-deb/usr/bin
ln -s ../lib/gmailnotify/gmailnotify.py build-deb/usr/bin/gmailnotify
ln -s ../lib/gmailnotify/gmailnotify-settings.py build-deb/usr/bin/gmailnotify-settings

mkdir -p build-deb/DEBIAN
cp DEBIAN/control build-deb/DEBIAN/
cp DEBIAN/prerm build-deb/DEBIAN/

dpkg -b build-deb gmailnotify-0.1-all.deb

rm -R build-deb
