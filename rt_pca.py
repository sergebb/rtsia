#! /usr/bin/python
import numpy as np
import scipy as sp
import sys
import re
from datetime import datetime

DEAL="deal.cvs"
ORDER="orders.txt" 

def main():

	df = open(DEAL,"r")
	of = open(ORDER,"r")

	for line in df:
		if line[0] == '#':
			continue
		date = line.split(',')[2]
		price = line.split(',')[4]
		val = line.split(',')[5]
		deal_type = line.split(',')[7]
		# print date, "\t", price, "\t", val, "\t", deal_type,
		t = datetime.strptime(date, "%Y%m%d%H%M%S%f")
		print t.strftime('%d/%m/%y %H:%M:%S.%f')




if __name__ == '__main__':
    main()
