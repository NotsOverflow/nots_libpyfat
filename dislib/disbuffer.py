#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

from disdefine import *
import os, copy

'''

	Load buffer class 
	
--------------------------------------------------------'''

class LoadBuffer:

	def __init__(self, filename, to_pos=0, from_pos=0, sector_size=SECTOR_SIZE, verb=VERBOSE):
		global VERBOSE
		VERBOSE = verb
	
		self.filename = filename
		self.sector_size = sector_size
		self.buffer = []
		self.buff_size = 0
		self._counter = 0
		self.size = 0
		
		self.loadSlice(from_pos,to_pos)
		
	
	def get_buffer(self):
		
		return self.buffer
		
	def backup_state(self):
		
		tmptuple = (\
					self.filename,\
					self.sector_size,\
					self.buffer,\
					self.buff_size,\
					self._counter,\
					self.size\
				)
		dcopy = copy.deepcopy(tmptuple)
		return dcopy
				
	def restore_state(self,value):
		
					self.filename,\
					self.sector_size,\
					self.buffer,\
					self.buff_size,\
					self._counter,\
					self.size\
				= value
		
	def populate_buffer(self,bpos,scount):
	
		if scount < 1:
			return self.buffer
		self.size = self.size + scount
		file = open(self.filename, "rb")
		file.seek(bpos * self.sector_size,0)
		while( scount > 0 ):
			self.buffer.append(map(ord,list(file.read(self.sector_size))))
			scount = scount - 1
		file.close()
		
		return self.buffer
		
	def loadSlice(self,from_pos=0,to_pos=0):

		size = os.stat(self.filename).st_size
		file_sectors = ( size / self.sector_size )
		from_pos = self.get_within_pos(from_pos,file_sectors)
		to_pos = self.get_within_pos(to_pos,file_sectors)
		
		if from_pos < to_pos :
			file_sectors = to_pos - from_pos
			return self.populate_buffer(from_pos, file_sectors )
		else :
			file_sectors = from_pos - to_pos
			return self.populate_buffer(to_pos, file_sectors )

	
	def flush_buffer(self):
		del self.buffer
		self.buffer = []
		self.size = 0
		return True
		
	def get_within_pos(self, number, bondary):
	
		if abs(number) > bondary :
			number = number % bondary
		if number < 0 :
			number = bondary + number 
				
		return number
		
	def new_buffer(self,to_pos=0,from_pos=0):
		self.flush_buffer()
		self.loadSlice(from_pos, to_pos)
		return self.buffer
		
	def __getitem__(self, key):
	
		if self.size == 0:
			return []
		return self.buffer[key]
		
	def __len__(self):
	
		return (self.slice[1] - self.slice[0]) 
		
	def __iter__(self):
	
		return self

