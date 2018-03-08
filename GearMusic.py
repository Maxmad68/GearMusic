#!/usr/bin/python
# -*- coding: utf-8 -*-


import mechanize
from mechanize import *
import time,datetime
from bs4 import *
import requests as requests_mod
import re
import os

#  Copyright 2018 Maxime MADRAU

__doc__ = """
	Simple library for adding, listing and removing musics on a Samsung Gear S2 or Gear S3 device.
	Technically, it's a wrapper of the "Gear Music Manager" web interface.
	"""

__author__ = 'Maxime Madrau (maxime@madrau.com)'

class UnacceptedConnexion(Exception):
	'''
	If gear reject connexion request
	''' 
	pass


class UnsupportedFile(Exception):
	'''
	Happens when you try to add a file that is not a music track on the gear
	'''
	pass

def bytes(str_):
	'''
	Converts a string formatted like "5.5 MB" to number of bytes 5500000
	'''
	size = float(re.findall(r'([0-9.]+)', str_)[0])
	unity = re.findall(r'([A-Z]+)', str_)[0]
	convertTable = {'bytes':1,'KB':1000,'MB':1000**2,'GB':1000**3}
	return int(size*convertTable[unity])
	
getExtension = lambda file:os.path.split(file)[1].split('.')[-1] #Returns extension of a file

class Track(object):
	'''
	Represents a music on the Gear.
	A Track object is initialized by a gear object and can be obtained in the GearInstance.musics list
	Attributes:
		path (basestring) : The path on the Gear
		format (basestring) : The format of the file
		title (basestring)
		artist (basestring)
		album (basestring)
		duration (datetime.timedelta)
		size (int) : In bytes
		parent : The Gear object
	
	'''
	def __init__(self,songParams,parent):
		self.path = songParams[0].findAll('input')[0]['value']
		self.format = getExtension(self.path)
		self.title = songParams[2].string
		self.artist = songParams[4].string
		self.album = songParams[6].string
		
		duration = map(int,songParams[8].string.split(':'))
		self.duration = datetime.timedelta( seconds=duration[-1], minutes=duration[-2] if len(duration) >= 2 else 0, hours=duration[-3] if len(duration) >= 3 else 0,days=duration[-4] if len(duration) >= 4  else 0)

		self.size = bytes(songParams[10].string)
		self.parent = parent
	
	def __repr__(self):
		return '<Track "%s" by "%s">'%(self.title,self.artist)

class Gear(object):
	'''
	Represents a Samsung Gear S2 or S3
	Parameters:
		ip (basestring) : The IP address of the Gear
		debug=False (bool) : If True, print debug messages on the connexion status
	Attributes:
		tracks (list [Track, ...]) : The list of all tracks on the watch
	'''
	
	def __init__(self,ip,debug=False):
		self.ip = ip.replace(':3000','')
		self.tracks = []
		self.br = mechanize.Browser()
		self.br.set_debug_http(False)
		self.br.set_debug_redirects(False)
		self.br.set_debug_responses(False)
		self.br.set_handle_robots(False)   # no robots
		self.br.set_handle_refresh(False)  # can sometimes hang without this
		self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
		self.br.open('http://%s:3000/list'%self.ip)
	
	def wait_for_connexion(self):
		'''
		When you initialize a Gear object by an ip, the device will ask you to accept or deny the connexion.
		Using this function will start a loop still you accept or deny the connexion on the watch.
		'''
		while True:
			self.br.open('http://%s:3000/list'%self.ip)
			now = self.br.response().read()
			if '<table' in now:
				break
		
		print 'Went Out'		
		self.load_tracks()
			
	def load_tracks(self):
		'''
		Reloads tracks list
		'''
		if self.br.response() == None:
			raise UnacceptedConnexion('Accept connexion on Gear before processing data')
		
		soup = BeautifulSoup(self.br.response().read(),'lxml')
		#print soup
		songTable = soup.findAll('tbody',{'class':'sub-content2'})[0]
		songTr = songTable.findAll('tr')
		id_ = -1
		for song in songTr:
			id_ += 1
			songParams = song.findAll('td')
			track = Track(songParams,self)
			track.id = id_
			self.tracks.append(track)
			
	def add_tracks(self,*files,**kwargs):
		'''
		Add tracks on the Gear.
		You can add multiple tracks by giving path of the files as arguments
		Files must have a .mp3, .m4a, .aac, .ogg or .wma extension.
		Parameters:
			- force=False (bool) : Force uploading of the files, doesn't care of the format.
			- *files (list [basestring, basestring, ...] ) : List of paths of tracks to add
		'''
		force = kwargs.get('force',False)
		for file in files:
			extension = getExtension(file)
			if extension in ('mp3','m4a','aac','ogg','wma') or force:
				files = {'upFiles':open(file,'rb')}
				values = {'fileCnt': 0, 'fileCntTotal': 1}
				r = requests_mod.post('http://%s:3000/upload'%self.ip,files=files, data=values)
			else:
				raise UnsupportedFile('%s is not a correct format'%extension)
				
		self.br.open('http://%s:3000/list'%self.ip)				
		self.load_tracks()
		
	def remove_tracks(self,*tracks):
		'''
		Remove tracks from the gear
		Parameters:
			*tracks (list [Track, Track, ...] ) : List of tracks to remove
		'''
		self.br.form = list(self.br.forms())[0] 
		for control in self.br.form.controls:
			if control.name == 'chkBox':
				checkboxControl = control
				
		for track in tracks:
			for cb in checkboxControl.get_items():
				if cb.id == 'chkBox%i'%track.id:
					checkbox = cb
					break
				
			cb.selected = True
			
		self.br.form.new_control('submit', 'Button', {})
		self.br.form.fixup()
		response = self.br.submit()
		
		self.br.open('http://%s:3000/list'%self.ip)
		self.load_tracks()
		
				
	add_track = add_tracks
	remove_track = remove_tracks
