#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

import disutil
from disdefine import *

'''

	Parse the mbr 
	
--------------------------------------------------------'''

class LoadMbr:
	def __init__(self, bufferObj, type_format="FAT"):
		if type_format != "FAT":
			raise "UnsiportedFileFormat"
		bufferObj.new_buffer(0,1)
		self.buffer = []
		self.sector =  bufferObj[0]
		self.populate_part_1()
		self.populate_calculations()
		self.populate_part_2()
		
	def populate_calculations(self):
	
		self["root_dir_sectors"] = 0
		
		if (self["root_entries_count"] != 0):
			self["root_dir_sectors"] = (\
										(self["root_entries_count"] * 32)\
										+ ( self["byts_per_sector"] - 1 )\
									)\
								    / self["byts_per_sector"]
			
		if ( self["total_sector_16"] != 0 ):
			self["total_sectors"] = self["total_sector_16"];
		else:
			self["total_sectors"] = self["total_sector_32"];
			
		if (self["fat_size_16"] != 0):
			self["fat_size"] = self["fat_size_16"]
		else:
			self["fat_size"] = self["fat_size_32"]
			
		#ajust partition here	
		self["first_data_sector"] = self["reserved_sector_count"]\
							   + ( self["num_fats"] * self["fat_size"] )\
							   + self["root_dir_sectors"]
		self["data_sector"] = self["total_sectors"] - self["first_data_sector"]
		self["count_of_clusters"] = self["data_sector"] / self["sector_per_cluster"]
		
		if self["count_of_clusters"] < 4085 :
			self["volume_type"] = "FAT12"
			self["fat_offset"] = 0
		elif self["count_of_clusters"] < 65525 :
			self["volume_type"] = "FAT16"
			self["fat_offset"] = 2
		else :
			self["volume_type"] = "FAT32"
			self["fat_offset"] = 4	
	
	def populate_part_1(self):
		sector = self.sector
		self.buffer.append(("jboot", disutil.ashex(disutil.make_string(sector[0:3]))))
		self.buffer.append(("oem_id", disutil.make_string(sector[3:11])))
		self.buffer.append(("byts_per_sector", disutil.toInt(sector[11:13])))
		self.buffer.append(("sector_per_cluster", disutil.toInt(sector[13:14])))
		self.buffer.append(("reserved_sector_count", disutil.toInt(sector[14:16])))
		self.buffer.append(("num_fats", disutil.toInt(sector[16:17])))
		self.buffer.append(("root_entries_count", disutil.toInt(sector[17:19])))		
		self.buffer.append(("total_sector_16", disutil.toInt(sector[19:21])))
		self.buffer.append(("media_type", disutil.toInt(sector[21:22])))
		self.buffer.append(("fat_size_16", disutil.toInt(sector[22:24])))
		self.buffer.append(("sectors_per_track", disutil.toInt(sector[24:26])))
		self.buffer.append(("number_heads", disutil.toInt(sector[26:28])))
		self.buffer.append(("hidden_sectors", disutil.toInt(sector[28:32])))	
		self.buffer.append(("total_sector_32", disutil.toInt(sector[32:36])))
		self.buffer.append(("fat_size_32", disutil.toInt(sector[36:40])))
		

	def populate_part_2(self):
		sector = self.sector
		fat_type = self["volume_type"]
		if (fat_type == "FAT12") or (fat_type == "FAT16"):
			#fatmagik = disutil.make_string(sector[54:62])
			#if((fatmagik != "FAT     ") 
			#or (fatmagik != "FAT12   ") 
			#or (fatmagik != "FAT16   ")):
			#	raise("BadFatMagik")
			self["fat_size_32"] = ("drive_number", disutil.ashex(disutil.make_string(sector[36:37])))
			#self.buffer.append(("drive_number", disutil.ashex(disutil.make_string(sector[36:37]))))
			self.buffer.append(("reserved1", disutil.toInt(sector[37:38])))
			self.buffer.append(("boot_signature", disutil.toInt(sector[38:39])))
			self.buffer.append(("volume_id",  disutil.ashex(disutil.make_string(sector[39:43]))))
			self.buffer.append(("volume_label", disutil.make_string(sector[43:54])))
			self.buffer.append(("file_system_type", disutil.make_string(sector[54:62])))
		elif fat_type == "FAT32":
			#fat32magik = disutil.make_string(sector[82:90])
			#if fat32magik != "FAT32   ":
			#	raise("BadFatMagik")
			#self.buffer.append(("fat_size_32", disutil.toInt(sector[36:40])))
			self.buffer.append(("extended_flags", disutil.ashex(disutil.make_string(sector[40:42]))))
			self.buffer.append(("file_system_version", disutil.ashex(disutil.make_string(sector[42:44]))))
			self.buffer.append(("root_cluster", disutil.toInt(sector[44:48])))
			self.buffer.append(("file_system_info", disutil.toInt(sector[48:50])))
			self.buffer.append(("book_boot_sector", disutil.toInt(sector[50:52])))
			self.buffer.append(("reserved", disutil.toInt(sector[52:64])))
			self.buffer.append(("drive_number", disutil.ashex(disutil.make_string(sector[64:65]))))
			self.buffer.append(("reserved1", disutil.toInt(sector[65:66])))
			self.buffer.append(("boot_signature", disutil.toInt(sector[66:67])))
			self.buffer.append(("volume_id", disutil.ashex(disutil.make_string(sector[67:71]))))
			self.buffer.append(("volume_label", disutil.make_string(sector[71:82])))
			self.buffer.append(("file_system_type", disutil.make_string(sector[82:90])))
		else:
			raise("NonFatFileSystem")
		
		self.buffer.append(("partition_1", disutil.ashex(disutil.make_string(sector[446:462]))))
		self.buffer.append(("partition_2", disutil.ashex(disutil.make_string(sector[462:478]))))
		self.buffer.append(("partition_3", disutil.ashex(disutil.make_string(sector[478:494]))))
		self.buffer.append(("partition_4", disutil.ashex(disutil.make_string(sector[494:510]))))
		
		self.buffer.append(("boot_close", disutil.ashex(disutil.make_string(sector[510:512]))))

	def __repr__(self):
		string = ""
		for index, value in enumerate(self.buffer):
			string = string + str(value[0]) + " -> " + str(value[1]) + " \n"
		return string
		
	def __getitem__(self, key):
		if type(key) == int:
			return self.buffer[key][1]
		elif type(key) == str:
			for index, value in enumerate(self.buffer):
				if ( value[0] ==  key) :
					return value[1]
		else:
			raise("InvalidParam")		
	def __setitem__(self, key, value):
		if type(key) == int:
			if type(value) == tuple:
				self.buffer[key] = value
				return self.buffer[key]
			else:
				self.buffer[key][1] = value
				return self.buffer[key][1]
		elif type(key) == str:
			for index, content in enumerate(self.buffer):
				if ( content[0] ==  key) :
					if type(value) == tuple:
						self.buffer[index] = value
						return self.buffer[index]
					else:
						self.buffer[index][1] = value
						return self.buffer[index][1]
				if type(value) == tuple:
					return self.buffer.append(value)
				else:
					return self.buffer.append((key, value))
				
			raise("KeyNotFound")
		else:
			raise("InvalidParam")



	
