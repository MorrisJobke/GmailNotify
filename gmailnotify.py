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

import gtk
import indicate
import time
import urllib2
import base64
import subprocess
import feedparser
import pynotify
import calendar
import gobject

# own class Keyring
from gmailnotifykeyring import Keyring 

GmailIcon = 'file:///usr/share/pixmaps/gmailnotify.svg'
GmailNotifyName = 'Google Mail Notify'

class GMailIndicator(indicate.Indicator):
	def __init__(self, title, sender, time, link=None, settings=False):
		""" indicator for a mail in inbox """
		indicate.Indicator.__init__(self)
		self.title = title
		self.sender = sender
		self.time = time
		self.link = link
		self.isSettingsIndicator = settings
		self.set_property('name', self.title)
		if not self.time == None:
			self.set_property_time('time', time)
		self.connect('user-display', self.click)
		self.stress()
		
	def stress(self):
		""" indicator marked as unread """
		self.set_property('draw-attention', 'true')
		
	def unstress(self):
		""" indicator marked as read """
		self.set_property('draw-attention', 'false')
	
	def click(self, server, something):
		""" called if indicator entry is clicked """
		self.unstress()
		if not self.link == None:
			subprocess.call(['gnome-open', self.link])
		elif self.isSettingsIndicator:
			self.openSettingsDialog()
	
	def openSettingsDialog(self):
		""" called if setting is not complete """
		subprocess.call(['gmailnotify-settings'])

class Notifier:
	def __init__(self, username, password):
		""" entry in indicator applet """ 
		self.timeout = 30
		self.server = indicate.indicate_server_ref_default()
		self.server.set_type('message.mail')
		self.server.set_desktop_file('/usr/lib/gmailnotify/gmailnotify.desktop')
		self.server.connect('server-display', self.click)
		
		self.request = urllib2.Request('https://mail.google.com/mail/feed/atom/')
		self.indicators = []
		
		if not username == None and not password == None: 		
			self.request.add_header('Authorization', 'Basic %s'%(base64.encodestring('%s:%s'%(username, password))[:-1]))
		
			indicator = GMailIndicator('Receiving data ...',  GmailNotifyName, time.time())
			self.indicators.append(indicator)
			self.indicators[-1].unstress()
			self.indicators[-1].show()
			self.checkMails()
		else:
			indicator = GMailIndicator('Setting up ' + GmailNotifyName, GmailNotifyName, None, None, True)
			self.indicators.append(indicator)
			self.indicators[-1].show()
			pynotify.Notification(GmailNotifyName, 'You have to set up ' + GmailNotifyName, GmailIcon).show()
		
	def click(self, server, something):
		""" called if entry is clicked """
		subprocess.call(['gnome-open', 'https://mail.google.com/'])
		
	def checkMails(self):
		""" check gmail for unread mails """
		print 'Receiving data ...'
		try:
			data = feedparser.parse(urllib2.urlopen(self.request).read())
		except:
			self.error = pynotify.Notification(GmailNotifyName, 'An error occured - May the login information is not valid', GmailIcon)
			self.error.show()
			indicator = GMailIndicator('Setting up ' + GmailNotifyName, GmailNotifyName, None, None, True)
			self.indicators.append(indicator)
			self.indicators[-1].show()
			
			deleteIndicators = []
		
			for i in self.indicators:
				if i.title in ['Receiving data ...']:
					deleteIndicators.append(i)
		else:
			for mail in data['entries']:
				if not mail['title'] in [indicator.title for indicator in self.indicators]:
					print 'new mail ...'
					i = GMailIndicator(
						mail['title'],
						mail['author_detail']['name'],
						time.mktime(time.localtime(calendar.timegm(time.strptime(mail['issued'].replace('T24', 'T00'),'%Y-%m-%dT%H:%M:%SZ')))),
						mail['link']
					) 
					self.indicators.append(i)
					self.indicators[-1].show()
								
					n = pynotify.Notification(
						mail['title'], 
						'from ' + mail['author_detail']['name'] + ' <' + mail['author_detail']['email'] + '>', 
						GmailIcon
					)
					n.show()
		
			deleteIndicators = []
		
			for i in self.indicators:
				if not i.title in [mail['title'] for mail in data['entries']]:
					deleteIndicators.append(i)
				
		for i in deleteIndicators:
			i.unstress()
			i.hide()
			self.indicators.remove(i)
		
		gobject.timeout_add_seconds(self.timeout, self.checkMails)
		
if __name__ == "__main__":	
	gkr = Keyring(GmailNotifyName, 'login data')
	username, password = gkr.getLogin()
	if username == '':
		username = None
	if password == '':
		password = None
	gmn = Notifier(username,password)
	gtk.main()
