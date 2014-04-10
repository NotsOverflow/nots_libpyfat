#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

import sys
import nl_disk_image as ndi

if __name__ == "__main__":

	usage = "\n\tusage %s -v <image_file> for verbose\n\tusage %s <image_file>\n" % (sys.argv[0],sys.argv[0])

	argc = len(sys.argv)
	if argc == 3:
		if sys.argv[1] != '-v':
			print(usage)
			quit()
	if argc != 2 and argc != 3:
		print(usage)
		quit()
	
	if sys.argv[1] == "-v":
		ndi.VERBOSE = True
		img = sys.argv[2]
	else:
		img = sys.argv[1]
		
	print("looking @ %s with verbose: %s" % (img, ndi.VERBOSE))
	disk = ndi.DiskImage(img);
	print disk.boot
	print disk
