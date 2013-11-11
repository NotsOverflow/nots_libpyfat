#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

import sys
import os
import util

SECTOR_SIZE = 512

class Disk:
	def __init__(self, filename):
		self.filename = filename
		self.image = DiskImage(filename)
		self.boot = PartitionBootSector(self.image[0])
		
class DiskImage:
	"""Abstraction of a disk image. Loads the entire image on memory"""
	def __init__(self, filename, sector_size=SECTOR_SIZE):
		self.filename = filename
		self.sector_size = sector_size
		self.buffer, self.size = self.loadFile(filename)
		self._counter = 0

	def loadFile(self, filename):
		'''Loads a file into an array of 512-byte sectors'''
		file = open(filename, "rb")
		buffer = []
			
		size = os.stat(filename).st_size
	
		for i in xrange(size/self.sector_size + 1):
			buffer.append(map(ord,list(file.read(self.sector_size))))
	
		file.close()
		return (buffer,i)
	
	def __getitem__(self, key):
		return self.buffer[key]
	
	def __iter__(self):
		return self

class PartitionBootSector:
	def __init__(self, sector):
		self.buffer = []
		
		fat32magik = util.make_string(sector[82:90])
		fatmagik = util.make_string(sector[54:62])
		
		
		if ( fat32magik == "FAT32   " ):
		
		
			self.buffer.append(("fat_size_32", util.toInt(sector[36:40])))
			self.buffer.append(("extended_flags", ashex(util.make_string(sector[40:42]))))
			self.buffer.append(("file_system_version", ashex(util.make_string(sector[42:44]))))
			self.buffer.append(("root_cluster", util.toInt(sector[44:48])))
			self.buffer.append(("file_system_info", util.toInt(sector[48:50])))
			self.buffer.append(("book_boot_sector", util.toInt(sector[50:52])))
			self.buffer.append(("reserved", util.toInt(sector[52:64])))
			self.buffer.append(("drive_number", ashex(util.make_string(sector[64:65]))))
			self.buffer.append(("reserved1", util.toInt(sector[65:66])))
			self.buffer.append(("boot_signature", util.toInt(sector[66:67])))
			self.buffer.append(("volume_id", ashex(util.make_string(sector[67:71]))))
			self.buffer.append(("volume_label", util.make_string(sector[71:82])))
			self.buffer.append(("file_system_type", util.make_string(sector[82:90])))
		
		elif((fatmagik == "FAT     ") 
			or (fatmagik == "FAT12   ") 
			or (fatmagik == "FAT16   ")):
		
			self.buffer.append(("drive_number", ashex(util.make_string(sector[36:37]))))
			self.buffer.append(("reserved1", util.toInt(sector[37:38])))
			self.buffer.append(("boot_signature", util.toInt(sector[38:39])))
			self.buffer.append(("volume_id",  ashex(util.make_string(sector[39:43]))))
			self.buffer.append(("volume_label", util.make_string(sector[43:54])))
			self.buffer.append(("file_system_type", util.make_string(sector[54:62])))
		else:
			raise("InvalidFatBootSector")
		
		#actually the begining of the boot sector info

		self.buffer.insert(0,("total_sector_32", util.toInt(sector[32:36])))
		self.buffer.insert(0,("hidden_sectors", util.toInt(sector[28:32])))
		self.buffer.insert(0,("number_heads", util.toInt(sector[26:28])))
		self.buffer.insert(0,("sectors_per_track", util.toInt(sector[24:26])))
		self.buffer.insert(0,("fat_size_16", util.toInt(sector[22:24])))
		self.buffer.insert(0,("media_type", util.toInt(sector[21:22])))
		self.buffer.insert(0,("total_sector_16", util.toInt(sector[19:21])))
		self.buffer.insert(0,("root_entries_count", util.toInt(sector[17:19])))
		self.buffer.insert(0,("num_fats", util.toInt(sector[16:17])))
		self.buffer.insert(0,("reserved_sector_count", util.toInt(sector[14:16])))
		self.buffer.insert(0,("sector_per_cluster", util.toInt(sector[13:14])))
		self.buffer.insert(0,("byts_per_sector", util.toInt(sector[11:13])))
		self.buffer.insert(0,("oem_id", util.make_string(sector[3:11])))
		self.buffer.insert(0,("jboot", ashex(util.make_string(sector[0:3]))))
		
		self.buffer.append(("boot_close", sector[510:512]))
		
		self.buffer.append(("the_sector", sector))


	def __repr__(self):
		string = ""
		for index, value in enumerate(self.buffer):
			string = string + str(value[0]) + " -> " + str(value[1]) + " \n"
		return string
		
	def __getitem__(self, key):
		if type(key) == int:
			return self.buffer[key][1]
		else:
			for index, value in enumerate(self.buffer):
				if ( value[0] ==  key) :
					return value[1]
		raise("InvalidParam")
		

def ashex(s):
	return ':'.join(x.encode('hex') for x in s)

if __name__ == "__main__":
	print("runing %s with %s as argument" % (sys.argv[0], sys.argv[1]))
	disk = Disk(sys.argv[1]);
	print disk.boot
