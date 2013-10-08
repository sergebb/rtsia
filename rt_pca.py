#! /usr/bin/python
import numpy as np
import scipy as sp
import sys
import re
from datetime import datetime
from datetime import timedelta

DEAL="deal.cvs"
ORDER="orders.txt" 

def pca(data):
	data = data - data.mean(axis=0)
	(u,s,v) = np.linalg.svd(data, full_matrices=False)
	return np.dot(data, v.T)

def main():

	df = open(DEAL,"r")
	of = open(ORDER,"r")

	orders = []
	deals = None
	i=0
	for line in df:
		i+=1
		if i> 10000:
			break
		if line[0] == '#':
			continue
		date = line.split(',')[2]
		price = int(line.split(',')[4].split('.')[0])
		val = int(line.split(',')[5])
		deal_type = line.split(',')[7]
		# print date, "\t", price, "\t", val, "\t", deal_type,
		deal_time = datetime.strptime(date, "%Y%m%d%H%M%S%f")
		while True:
			ordline = of.readline()
			if ordline[0] == '#':
				continue
			ord_time = datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f")
			orders.append(ord_time)
			if(ord_time>deal_time):
				break
		# time1 = datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
		time1 = timedelta(seconds=1)
		time2 = timedelta(seconds=10)
		time3 = timedelta(seconds=60)
		for i in range(len(orders)-1,0,-1):
			num = len(orders) - i
			if(orders[i]+time1<deal_time):
				c1=num
				break
		for i in range(len(orders)-1,0,-1):
			num = len(orders) - i
			if(orders[i]+time2<deal_time):
				c2=num
				break
		for i in range(len(orders)-1,0,-1):
			num = len(orders) - i
			if(orders[i]+time3<deal_time):
				c3=num
				break
		newdata = [int(deal_time.second),price,val,c1,c2,c3]
		if deals == None:
			deals = newdata
		else:
			deals = np.vstack((deals, newdata))
        	# print deals
	
	A = pca(deals)

	for r in A:
		print "%.04f\t%.04f\t%d" % (r[0], r[1],1)
		# print [deal_time,price,val,c1,c2,c3]

	# for line in of:
	# 	if line[0] == '#':
	# 		continue
	# 	date = line.split(',')[3]
	# 	t = datetime.strptime(date, "%Y%m%d%H%M%S%f")
	# 	orders.append(t)







if __name__ == '__main__':
    main()
