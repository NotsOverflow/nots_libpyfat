#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

from disdefine import *

class LoadTools:
	def __init__(self,bufferObj,bootObj):
		self.bootObj = bootObj
		self.bufferObj = bufferObj

	def nf_get_cluster_offsets(self,cluster=0):
	
		fat_offset = self.bootObj["fat_offset"]
		if fat_offset == 0:
			fat_offset = cluster + (cluster / 2) 
		elif fat_offset == 2 or fat_offset == 4:
			fat_offset = cluster * fat_offset
		else:
			raise "WrongOffset"
			
		this_fat_sector_number = self.bootObj["reserved_sector_count"]\
							   + ( fat_offset / self.bootObj["byts_per_sector"])
		this_fat_entrie_offset = fat_offset % self.bootObj["byts_per_sector"]
		
		return (this_fat_sector_number,this_fat_entrie_offset)

	def fetsh_cluster(self,cluster):
	
		tfsn , tfeo = nf_get_cluster_offsets(cluster)
		self.bufferObj.new_buffer(\
								  from_pos=(tfsn+tfeo),\
								  to_pos=(tfsn+tfeo) \
								  + self.bootObj["sector_per_cluster"]\
								  + 1 \
								 )
		return True
		
	def read_buffer_line12(self,line=0,buffer_line=0):
	
		info = self.bufferObj[buffer_line][line]
		
		if ( line & "\x00\x01") :
			return info >> 4
		else:
			return info & "\x0F\xFF"

		
	def read_buffer_line16(self,line=0,buffer_line=0):
	
			return self.bufferObj[buffer_line][line]
			
	def read_buffer_line32(self,line=0,buffer_line=0):

			return self.bufferObj[buffer_line][line:line+1] & "\x0F\xFF\xFF\xFF"

		
	def is_EOF(self,cluster=0):
		content = read_cluster_content(cluster)
		isEOF = False
		if self.fat_offset == 0 :
			if content >= "\x0F\xF8":
				isEOF = True
		elif self.fat_offset == 2 :
			if content >= "\xFF\xF8":
				isEOF = True
		elif self.fat_offset == 4 :
			if content >= "\x0F\xFF\xFF\xF8":
				isEOF = True
		else:
			rise("WrongOffsetFileSystem")
		return isEOF
		
	def is_bad_cluster(self,cluster=0):
		content = read_cluster_content(cluster)
		is_bc = False
		if self.fat_offset == 0 :
			if content >= "\x0F\xF7":
				is_bc = True
		elif self.fat_offset == 2 :
			if content >= "\xFF\xF7":
				is_bc = True
		elif self.fat_offset == 4 :
			if content >= "\x0F\xFF\xFF\xF7":
				is_bc = True
		else:
			rise("WrongOffsetFileSystem")
		return is_bc
		
	def set_line_content12(self,buffer_line,line,content):
		
		if ( line & "\x00\x01") :
			content = content[-2:] << 4
			temp = self.bufferObj[buffer_line][line] & "\x00\x0F"
		else:
			content = content[-2:] & "\x0F\xFF"
			temp = self.bufferObj[buffer_line][line] & "\xF0\x00"
		self.bufferObj[buffer_line][line] = temp | content[-2:]
		
		return self.bufferObj[buffer_line][line]
	
	def set_line_content16(self,buffer_line,line,content):
		
		self.bufferObj[buffer_line][line] = content[-2:]
		
		return self.bufferObj[buffer_line][line]
	
	def set_line_content32(self,buffer_line,line,content):
	
		temp = self.bufferObj[buffer_line][line]
		
		sector_state = temp & "\xF0\x00\x00\x00"
		sector_content = temp & "\x0F\xFF\xFF\xFF"
		
		self.bufferObj[buffer_line][line] = sector_state | sector_content
		
		return self.bufferObj[buffer_line][line]
