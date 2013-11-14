#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

import nl_disk_image as ndi

if __name__ == "__main__":
	print("runing %s with %s as argument" % (sys.argv[0], sys.argv[1]))
	disk = ndi.DiskImage(sys.argv[1]);
	print disk.boot
	print disk
