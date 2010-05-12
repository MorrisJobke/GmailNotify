#!/usr/bin/env python
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

import pygtk
import gtk
import urllib2
import base64
import gobject

# own class Keyring
from gmailnotifykeyring import Keyring 

GmailNotifyName = 'Google Mail Notify'

class GMailNotifySettings:
	def __init__(self):
		self.gladeFile = '/usr/share/applications/gmailnotify-settings.glade'
		self.valid = False
		self.initialisation = True
		self.timeouts = 0
		builder = gtk.Builder()	
		builder.add_from_file(self.gladeFile)
		builder.connect_signals({
			'on_settings_destroy': 			self.quit,  
			'on_close_clicked': 			self.quit, 
			'gtk_main_quit': 				self.quit,
			'on_apply_clicked': 			self.save,
			'on_entry_username_changed':	self.refreshTimeout,
			'on_entry_password_changed':	self.refreshTimeout,
		})
		
		self.window = builder.get_object('settings')
		self.aboutName = builder.get_object('name')
		self.aboutVersion = builder.get_object('version')
		self.entryUsername = builder.get_object('entry_username')
		self.entryPassword = builder.get_object('entry_password')
		self.validation = builder.get_object('validation')
		self.validationImage = builder.get_object('validation_image')
		self.gkr = Keyring(GmailNotifyName, 'login data')
		self.loadSettings()
		#self.naming()
		self.initialisation = False
		self.window.show()	
		self.refresh()
			
	def naming(self):
		""" prevent incorrect naming (ugly way) """
		self.window.set_title(GmailNotifyName + ' Settings')
		self.aboutName.set_text(GmailNotifyName)
		self.aboutVersion.set_text('Version ' + '0.1')
			
	def save(self, widget=None):
		""" save settings to keyring """
		print 'save settings'		
		if self.valid == True:
			print 'valid'
		else:
			print 'not valid'
		self.gkr.setLogin(self.entryUsername.get_text(), self.entryPassword.get_text())		
	
	def quit(self, widget):
		""" save settings and close window """
		print 'quit settings dialog'
		self.save()
		gtk.main_quit()
	
	def loadSettings(self):		
		""" load login information if already saved to keyring """
		username, password = self.gkr.getLogin()
		if not username == None:
			self.entryUsername.set_text(username)
		if not password == None:		
			self.entryPassword.set_text(password)
			
	def refreshTimeout(self, widget=None):
		""" initialize timeout - prevent check login information after every type in """
		if self.initialisation:
			return
		self.validationImage.set_from_stock('gtk-refresh', gtk.ICON_SIZE_SMALL_TOOLBAR)
		self.validation.set_text('Checking ...')
		self.timeouts += 1
		gobject.timeout_add(700, self.refresh)
	
	def refresh(self):	
		""" initiates validation check """
		if self.initialisation:
			return
			
		if self.timeouts > 1:
			self.timeouts -= 1
			return
		
		self.timeouts = 0
		
		print 'refresh validation'
		self.setValid(False)
		
		if self.entryUsername.get_text() == '' or self.entryPassword.get_text() == '':
			return
			
		self.validLoginInformation()
			
	def setValid(self, value):
		""" sets icon and text if valid or not """
		if value:
			self.valid = True
			self.validation.set_text('Valid login information')
			self.validationImage.set_from_stock('gtk-yes', gtk.ICON_SIZE_SMALL_TOOLBAR)
		else:
			self.valid = False
			self.validation.set_text('Invalid login information')
			self.validationImage.set_from_stock('gtk-dialog-error', gtk.ICON_SIZE_SMALL_TOOLBAR)
			
	def validLoginInformation(self):
		""" check if login information is valid """
		request = urllib2.Request('https://mail.google.com/mail/feed/atom/')
		request.add_header('Authorization', 'Basic %s'%(base64.encodestring('%s:%s'%(self.entryUsername.get_text(), self.entryPassword.get_text()))[:-1]))
		try:
			urllib2.urlopen(request)
			self.setValid(True)
		except urllib2.HTTPError:
			self.setValid(False)

if __name__ == "__main__":
	gmns = GMailNotifySettings()
	gtk.main()
