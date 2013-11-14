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
			
		bufferObj_bkp = bufferObj.backup_state()
		
		self.buffer = []
		self.sector =  bufferObj.new_buffer(0,1)[0]
		self.bufferObj = bufferObj
		self.populate_part_1()
		self.populate_calculations1()
		self.populate_part_2()
		self.populate_calculations2()
		self.load_fsinfo_sector()
		self.load_backup()
		
		bufferObj.restore_state(bufferObj_bkp)
			
	def load_backup(self, prefix = ""):
		if self[prefix + "volume_type"] != "FAT32" :
			return False
		bkp_pos = self[prefix + "book_boot_sector"]
		self.sector =  self.bufferObj.new_buffer(bkp_pos,bkp_pos + 1)[0]
		self.populate_part_1(prefix + "bkp_")
		self.populate_calculations1(prefix + "bkp_")
		self.populate_part_2(prefix + "bkp_")
		self.populate_calculations2(prefix + "bkp_")
		self.load_fsinfo_sector(prefix + "bkp_",bkp_pos+1)
	
	def load_fsinfo_sector(self, prefix = "",fsi_pos = -1):
		if self[prefix + "volume_type"] != "FAT32" :
			return False
		if fsi_pos < 0:
			fsi_pos = self[prefix + "file_system_info"]
		sector = self.bufferObj.new_buffer(fsi_pos,fsi_pos+1)[0]
		self.buffer.append((prefix + "fsi_lead_signature", disutil.ashex(disutil.make_string(sector[0:4]),1)))
		self.buffer.append((prefix + "fsi_reserved1", disutil.ashex(disutil.make_string(sector[4:484]))))
		self.buffer.append((prefix + "fsi_struc_sig", disutil.ashex(disutil.make_string(sector[484:488]),1)))
		self.buffer.append((prefix + "fsi_free_count", disutil.toInt(sector[488:492])))
		self.buffer.append((prefix + "fsi_next_free", disutil.toInt(sector[492:496])))
		self.buffer.append((prefix + "fsi_reserved2", disutil.ashex(disutil.make_string(sector[496:508]))))
		self.buffer.append((prefix + "fsi_boot_close", disutil.ashex(disutil.make_string(sector[508:512]),1)))
		if self[prefix + "fsi_lead_signature"] != "41:61:52:52":
			raise "BadFSInfoSignature"
		if self[prefix + "fsi_struc_sig"] != "61:41:72:72":
			raise "BadFSInfoStructSignature"
		if self[prefix + "fsi_boot_close"] != "aa:55:00:00":
			raise "BadFSInfoBootClose"
		
	def populate_calculations2(self, prefix = ""):
		if self[prefix + "boot_close"] != "aa:55":
			raise "NoBootClose"
		if self[prefix + "boot_signature"] != "29":
			raise "WrongBootSignature"
		if self[prefix + "volume_type"] is not "FAT32" :
			self[prefix + "root_dir_LBA"] = (\
								  (\
									self[prefix + "root_cluster"]\
									- 2 \
								  )\
								  * self[prefix + "sector_per_cluster"]\
								 )\
								 + self[prefix + "first_data_sector"]
			self[prefix + "root_dir_cluster_nbr"] = self[prefix + "root_cluster"]
		else :
			self[prefix + "root_dir_LBA"] = \
							   self[prefix + "reserved_sector_count"]\
							   + ( self[prefix + "num_fats"] * self[prefix + "fat_size"] )
			self[prefix + "root_dir_cluster_nbr"] = 0
		
	def populate_calculations1(self, prefix = ""):
	
		self[prefix + "root_dir_sectors"] = 0
		
		if (self[prefix + "root_entries_count"] != 0):
			self[prefix + "root_dir_sectors"] = (\
										(self[prefix + "root_entries_count"] * 32)\
										+ ( self[prefix + "byts_per_sector"] - 1 )\
									)\
								    / self[prefix + "byts_per_sector"]
			
		if ( self[prefix + "total_sector_16"] != 0 ):
			self[prefix + "total_sectors"] = self[prefix + "total_sector_16"];
		else:
			self[prefix + "total_sectors"] = self[prefix + "total_sector_32"];
			
		if (self[prefix + "fat_size_16"] != 0):
			self[prefix + "fat_size"] = self[prefix + "fat_size_16"]
		else:
			self[prefix + "fat_size"] = self[prefix + "fat_size_32"]
			
		#ajust partition here	
		self[prefix + "first_data_sector"] = self[prefix + "reserved_sector_count"]\
							   + ( self[prefix + "num_fats"] * self[prefix + "fat_size"] )\
							   + self[prefix + "root_dir_sectors"]
		self[prefix + "data_sector"] = self[prefix + "total_sectors"] - self[prefix + "first_data_sector"]
		self[prefix + "count_of_clusters"] = self[prefix + "data_sector"] / self[prefix + "sector_per_cluster"]
		
		if self[prefix + "count_of_clusters"] < 4085 :
			self[prefix + "volume_type"] = "FAT12"
			self[prefix + "fat_offset"] = 0
		elif self[prefix + "count_of_clusters"] < 65525 :
			self[prefix + "volume_type"] = "FAT16"
			self[prefix + "fat_offset"] = 2
		else :
			self[prefix + "volume_type"] = "FAT32"
			self[prefix + "fat_offset"] = 4	
	
		
	
	def populate_part_1(self,prefix = ""):
		sector = self.sector
		self.buffer.append((prefix + "jboot", disutil.ashex(disutil.make_string(sector[0:3]))))
		self.buffer.append((prefix + "oem_id", disutil.make_string(sector[3:11])))
		self.buffer.append((prefix + "byts_per_sector", disutil.toInt(sector[11:13])))
		self.buffer.append((prefix + "sector_per_cluster", disutil.toInt(sector[13:14])))
		self.buffer.append((prefix + "reserved_sector_count", disutil.toInt(sector[14:16])))
		self.buffer.append((prefix + "num_fats", disutil.toInt(sector[16:17])))
		self.buffer.append((prefix + "root_entries_count", disutil.toInt(sector[17:19])))		
		self.buffer.append((prefix + "total_sector_16", disutil.toInt(sector[19:21])))
		self.buffer.append((prefix + "media_type", disutil.ashex(disutil.make_string(sector[21:22]),1)))
		self.buffer.append((prefix + "fat_size_16", disutil.toInt(sector[22:24])))
		self.buffer.append((prefix + "sectors_per_track", disutil.toInt(sector[24:26])))
		self.buffer.append((prefix + "number_heads", disutil.toInt(sector[26:28])))
		self.buffer.append((prefix + "hidden_sectors", disutil.toInt(sector[28:32])))	
		self.buffer.append((prefix + "total_sector_32", disutil.toInt(sector[32:36])))
		self.buffer.append((prefix + "fat_size_32", disutil.toInt(sector[36:40])))
		

	def populate_part_2(self,prefix = ""):
		sector = self.sector
		fat_type = self[prefix + "volume_type"]
		if (fat_type == "FAT12") or (fat_type == "FAT16"):
			#fatmagik = disutil.make_string(sector[54:62])
			#if((fatmagik != "FAT     ") 
			#or (fatmagik != "FAT12   ") 
			#or (fatmagik != "FAT16   ")):
			#	raise("BadFatMagik")
			self[prefix + "fat_size_32"] = ("drive_number", disutil.ashex(disutil.make_string(sector[36:37])))
			#self.buffer.append((prefix + "drive_number", disutil.ashex(disutil.make_string(sector[36:37]))))
			self.buffer.append((prefix + "reserved1", disutil.toInt(sector[37:38])))
			self.buffer.append((prefix + "boot_signature", disutil.ashex(disutil.make_string(sector[38:39]),1)))
			self.buffer.append((prefix + "volume_id",  disutil.ashex(disutil.make_string(sector[39:43]),1)))
			self.buffer.append((prefix + "volume_label", disutil.make_string(sector[43:54])))
			self.buffer.append((prefix + "file_system_type", disutil.make_string(sector[54:62])))
		elif fat_type == "FAT32":
			#fat32magik = disutil.make_string(sector[82:90])
			#if fat32magik != "FAT32   ":
			#	raise("BadFatMagik")
			#self.buffer.append((prefix + "fat_size_32", disutil.toInt(sector[36:40])))
			self.buffer.append((prefix + "extended_flags", disutil.ashex(disutil.make_string(sector[40:42]))))
			self.buffer.append((prefix + "file_system_version", disutil.ashex(disutil.make_string(sector[42:44]))))
			self.buffer.append((prefix + "root_cluster", disutil.toInt(sector[44:48])))
			self.buffer.append((prefix + "file_system_info", disutil.toInt(sector[48:50])))
			self.buffer.append((prefix + "book_boot_sector", disutil.toInt(sector[50:52])))
			self.buffer.append((prefix + "reserved", disutil.toInt(sector[52:64])))
			self.buffer.append((prefix + "drive_number", disutil.ashex(disutil.make_string(sector[64:65]))))
			self.buffer.append((prefix + "reserved1", disutil.toInt(sector[65:66])))
			self.buffer.append((prefix + "boot_signature", disutil.ashex(disutil.make_string(sector[66:67]),1)))
			self.buffer.append((prefix + "volume_id", disutil.ashex(disutil.make_string(sector[67:71]),1)))
			self.buffer.append((prefix + "volume_label", disutil.make_string(sector[71:82])))
			self.buffer.append((prefix + "file_system_type", disutil.make_string(sector[82:90])))
		else:
			raise("NonFatFileSystem")
		
		self.buffer.append((prefix + "partition_1", disutil.ashex(disutil.make_string(sector[446:462]))))
		self.buffer.append((prefix + "partition_2", disutil.ashex(disutil.make_string(sector[462:478]))))
		self.buffer.append((prefix + "partition_3", disutil.ashex(disutil.make_string(sector[478:494]))))
		self.buffer.append((prefix + "partition_4", disutil.ashex(disutil.make_string(sector[494:510]))))
		
		self.buffer.append((prefix + "boot_close", disutil.ashex(disutil.make_string(sector[510:512]),1)))

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



	
