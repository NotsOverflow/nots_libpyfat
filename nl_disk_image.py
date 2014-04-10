#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

SECTOR_SIZE = 512

import sys
from dislib.distools import *
from dislib.disbuffer import *
from dislib.dismbr import *
from dislib.disdefine import *



class DiskImage:
	def __init__(self, filename, type_img="FAT"):
		self.filename = filename
		self.buffer = LoadBuffer(filename, verb=VERBOSE)
		self.boot = LoadMbr(self.buffer,type_img, verb=VERBOSE)
		self.tools = LoadTools(self.buffer,self.boot, verb=VERBOSE)
		
		
	def __repr__(self):
	
		represent = [
			("volume type", self.boot["volume_type"]),
			("fat offset", self.boot["fat_offset"]),
			("root_dir_sectors",self.boot["root_dir_sectors"]),
			("first data sector", self.boot["first_data_sector"]),			
			("total data sectors", self.boot["data_sector"]),
			("count_of_clusters", self.boot["count_of_clusters"])
		]
		string = ""
		for index, value in enumerate(represent):
			string = string + str(value[0]) + " -> " + str(value[1]) + " \n"
		return string
		
