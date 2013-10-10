#! /usr/bin/python
import numpy as np
import scipy as sp
import sys
import re
from datetime import datetime
from datetime import timedelta
import time

DEAL="deal.cvs"
ORDER="orders.txt" 
N = 10000
DIFF = 30

def pca(data):
	data = data - data.mean(axis=0)
	(u,s,v) = np.linalg.svd(data, full_matrices=False)
	return np.dot(data, v.T)

def Extremes(data_price):
	minpoints = []
	maxpoints = []
	lastmax = lastmin = 1
	lookMax = True
	lastIsMax = True
	diff = DIFF
	for i in range(1,len(data_price)-1):
		if data_price[i] > data_price[i-1] and data_price[i] > data_price[i+1] and lookMax == True:
			lookMax = False

			if data_price[i] - lastmin > diff:
				if len(maxpoints)>0 and lastIsMax == True and lastmax < data_price[i]:
					maxpoints.pop()
					maxpoints.append(i)
					lastmax = data_price[i]
					lastIsMax = True
				elif len(maxpoints)==0 or lastIsMax == False:
					maxpoints.append(i)
					lastmax = data_price[i]
					lastIsMax = True
		if data_price[i] < data_price[i-1] and data_price[i] < data_price[i+1] and lookMax == False:
			lookMax = True

			if lastmax - data_price[i] > diff:
				if len(minpoints)>0 and lastIsMax == False and lastmin > data_price[i]:
					minpoints.pop()
					minpoints.append(i)
					lastmin = data_price[i]
					lastIsMax = False
				elif len(minpoints)==0 or lastIsMax == True:
					minpoints.append(i)
					lastmin = data_price[i]
					lastIsMax = False

	return maxpoints,minpoints

def main():

	df = open(DEAL,"r")
	of = open(ORDER,"r")

	order_time = []
	ord_values = []
	deals = None
	line_num=0
	color = np.zeros(N)
	data_price =[]
	data_time = []
	for line in df:
		line_num+=1
		if line_num> N:
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
			order_time.append(ord_time)
			ord_values.append(int(ordline.split(',')[7]))
			if(ord_time>deal_time):
				break

		# time1 = datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
		time1 = timedelta(microseconds=100)
		time2 = timedelta(seconds=1)
		time3 = timedelta(seconds=2)
		time4 = timedelta(seconds=5)
		c1 = c2 = c3 = c4 = 0
		v1 = v2 = v3 = v4 = 0
		num = 0
		for i in range(len(order_time)-1,0,-1):
			num += ord_values[i]
			if order_time[i]+time1<deal_time and c1==0:	c1=num
			if order_time[i]+time2<deal_time and c2==0: c2=num
			if order_time[i]+time3<deal_time and c3==0: c3=num
			if order_time[i]+time4<deal_time and c4==0:	
				c4=num
				break

		for i in range(len(data_price)-1,0,-1):
			if data_time[i]+time1<deal_time and v1==0:	v1 = price - data_price[i]
			if data_time[i]+time2<deal_time and v2==0:	v2 = price - data_price[i]
			if data_time[i]+time3<deal_time and v3==0:	v3 = price - data_price[i]
			if data_time[i]+time4<deal_time and v4==0:	
				v4 = price - data_price[i]
				break
		# newdata = [time.mktime(deal_time.timetuple()),price,val,c1,c2,c3]
		newdata = [c1,c2,c3,c4,v1,v2,v3,v4]
		# print time.mktime(deal_time.timetuple())
		if deals == None:
			deals = newdata
		else:
			deals = np.vstack((deals, newdata))

		data_price.append(price)
		data_time.append(deal_time)
		
	maxpoints,minpoints = Extremes(data_price)

	# print maxpoints
	# print minpoints


	for i in maxpoints:
		color[i] = 3
		j=i
		time1 = timedelta(microseconds=100)
		while order_time[j]+time1>order_time[i] and j>0:
			j-=1
			color[j] = 2
		time1 = timedelta(seconds=1)
		while order_time[j]+time1>order_time[i] and j>0:
			j-=1
			color[j] = 1
	for i in minpoints:
		color[i] = -3
		j=i
		time1 = timedelta(microseconds=100)
		while order_time[j]+time1>order_time[i] and j>0:
			j-=1
			color[j] = -2
		time1 = timedelta(seconds=1)
		while order_time[j]+time1>order_time[i] and j>0:
			j-=1
			color[j] = -1

	A = pca(deals)
	i = 0
	for r in A:
		print "%.04f\t%.04f\t%d" % (r[0], r[1],color[i])
		i+=1
		# print [deal_time,price,val,c1,c2,c3]

	# for line in of:
	# 	if line[0] == '#':
	# 		continue
	# 	date = line.split(',')[3]
	# 	t = datetime.strptime(date, "%Y%m%d%H%M%S%f")
	# 	order_time.append(t)







if __name__ == '__main__':
	main()
