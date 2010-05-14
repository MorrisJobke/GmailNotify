#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Morris Jobke 2010 <morris.jobke@googlemail.com>
# 
# GMailNotify is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# GMailNotify is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import gnomekeyring
import gconf

class Keyring:
	def __init__(self, appName, appDescription):
		self.keyring = gnomekeyring.get_default_keyring_sync()
		self.appName = appName
		self.appDescription = appDescription
		self.gconfKey = '/apps/gnome-python-desktop/keyring_auth_token'
		self.dividingSymbol = ' '

	def getLogin(self):
		keyring = gnomekeyring.get_default_keyring_sync()
		authToken = gconf.client_get_default().get_int(self.gconfKey)
		if authToken > 0:
			try:
				secret = gnomekeyring.item_get_info_sync(keyring, authToken).get_secret()
			except gnomekeyring.DeniedError:
				login = None
				password = None
			else:
				try:
					login, password = secret.split(self.dividingSymbol)
				except:
					login = None
					password = None
		else:
			login = None
			password = None
		
		return login, password
		
	def setLogin(self, login, password):
		authToken = gnomekeyring.item_create_sync(
			self.keyring,
			gnomekeyring.ITEM_GENERIC_SECRET,
			'%s, %s'%(self.appName, self.appDescription),
			dict(appname='%s, %s'%(self.appName, self.appDescription)),
			self.dividingSymbol.join((login, password)), 
			True
		)
		gconf.client_get_default().set_int(self.gconfKey, authToken)
