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
LIMIT = 30

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

def Normalize(deals):
	N = deals.shape[0]
	c_b_norm = np.amax(deals[:,0:4])/100.0
	c_s_norm = np.amax(deals[:,4:8])/100.0
	v_norm = np.amax(deals[:,8:12])/100.0
	a_norm = np.amax(deals[:,12:16])/100.0
	cp_norm = np.amax(deals[:,16])/100.0
	ord_gap_norm = np.amax(deals[:,17])/100.0

	for i in range(N):
		for j in range(4):
			deals[i,j]/=c_b_norm
			deals[i,j+4]/=c_s_norm
			deals[i,j+8]/=v_norm
			deals[i,j+12]/=a_norm
		deals[i,16]/=cp_norm
		deals[i,17]/=ord_gap_norm
	return deals

def CenterPrice(deal_price):
	limit1 = min(LIMIT,(len(deal_price)-1)/2)
	limit2 = len(deal_price) - limit1
	if limit2 > limit1:
		fftdata = np.fft.fft(deal_price)
		for i in range(limit1,limit2):
			fftdata[i] = 0
			fftdata[-i] = 0
		fildata = np.fft.ifft(fftdata)

		return np.real(fildata[-1])
	else:
		return deal_price[-1]

def main():

	df = open(DEAL,"r")
	of = open(ORDER,"r")

	order_time_buy = []
	ord_values_buy = []
	order_time_sell = []
	ord_values_sell = []

	deals = None
	line_num=0
	color = np.zeros(N)
	data_price =[]
	data_time = []

	orders_time = []
	orders_type = []
	orders_price = []
	orders_value = []
	orders_action = []

	order_prev_len = 0 # start with zero position

	deal_prev_time = 0


	max_price = 207925
	min_price = 168075

	spect_buy = np.zeros(max_price - min_price+1)
	spect_sell = np.zeros(max_price - min_price+1)

	for line in df:
		line_num+=1
		# sys.stderr.write("%d\n"%line_num)
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
		if deal_prev_time == 0:
			deal_prev_time = deal_time

		while True:
			ordline = of.readline()
			if ordline[0] == '#':
				continue
			orders_time.append( datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f") )
			orders_type.append( ordline.split(',')[2] )
			orders_price.append( int(ordline.split(',')[6].split('.')[0]) )
			orders_value.append( int(ordline.split(',')[7]) )
			orders_action.append( int(ordline.split(',')[5]) )

			if orders_action == 1:
				change_val = 1*orders_value
			else:
				change_val = -1*orders_value

			if ordline.split(',')[2] == 'B':
				ord_time_buy = datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f")
				order_time_buy.append(ord_time_buy)
				ord_values_buy.append(int(ordline.split(',')[7]))

				if(ord_time_buy>deal_time):
					break
			elif ordline.split(',')[2] == 'S':
				ord_time_sell = datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f")
				order_time_sell.append(ord_time_sell)
				ord_values_sell.append(int(ordline.split(',')[7]))

				if(ord_time_sell>deal_time):
					break

		time_empty = timedelta(seconds = 30)
		while True:
			if order_time_buy[0] + time_empty < deal_time:
				order_time_buy.pop(0)
				ord_values_buy.pop(0)
			else: break
		while True:
			if order_time_sell[0] + time_empty < deal_time:
				order_time_sell.pop(0)
				ord_values_sell.pop(0)
			else: break

		for i in range(order_prev_len, len(orders_price)):
			if orders_action[i] == 1:
				change = 1
			else:
				change = -1
			if orders_type[i] == 'B':
				spect_buy[orders_price[i] - min_price]+=change*orders_value[i]
			elif orders_type[i] == 'S':
				spect_sell[orders_price[i] - min_price]+=change*orders_value[i]

		order_prev_len = len(orders_price) #used on next step

		idx = range(len(spect_buy))

		ord_sell_min = 0
		ord_buy_max = 0
		ord_pull_gap= 0

		for i in range(len(spect_sell)):
			if spect_sell[i]>0:
				ord_sell_min = i
				break
		for i in range(len(spect_sell)-1,0,-1):
			if spect_buy[i]>0:
				ord_buy_max = i
				break
		ord_pull_gap = ord_sell_min - ord_buy_max
		

		# time1 = datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
		time1 = timedelta(microseconds=200)
		time2 = timedelta(microseconds=500)
		time3 = timedelta(seconds=1)
		time4 = timedelta(seconds=3)
		c1b = c2b = c3b = c4b = 0
		c1s = c2s = c3s = c4s = 0
		v1 = v2 = v3 = v4 = 0
		p1 = p2 = p3 = p4 = 0
		a1 = a2 = a3 = a4 = 0
		num = 0
		for i in range(len(order_time_buy)-1,0,-1):
			num += ord_values_buy[i]
			if order_time_buy[i]+time1<deal_time and c1b==0: c1b=num
			if order_time_buy[i]+time2<deal_time and c2b==0: c2b=num
			if order_time_buy[i]+time3<deal_time and c3b==0: c3b=num
			if order_time_buy[i]+time4<deal_time and c4b==0:	
				c4b=num
				break
		for i in range(len(order_time_sell)-1,0,-1):
			num += ord_values_sell[i]
			if order_time_sell[i]+time1<deal_time and c1s==0: c1s=num
			if order_time_sell[i]+time2<deal_time and c2s==0: c2s=num
			if order_time_sell[i]+time3<deal_time and c3s==0: c3s=num
			if order_time_sell[i]+time4<deal_time and c4s==0:	
				c4s=num
				break

		for i in range(len(data_price)-1,0,-1):
			if data_time[i]+time1<deal_time and v1==0:
				p1 = data_price[i]
				v1 = price - p1
			if data_time[i]+time2<deal_time and v2==0:
				p2 = data_price[i]
				v2 = price - p2
			if data_time[i]+time3<deal_time and v3==0:
				p3 = data_price[i]
				v3 = price - p3
			if data_time[i]+time4<deal_time and v4==0:
				p4 = data_price[i]
				v4 = price - p4
				break

		for i in range(len(data_price)-1,0,-1):
			if data_time[i]+time1*2<deal_time and a1==0:	
				a1 = price + data_price[i] - 2*p1
			if data_time[i]+time2*2<deal_time and a2==0:
				a2 = price + data_price[i] - 2*p2
			if data_time[i]+time3*2<deal_time and a3==0:
				a3 = price + data_price[i] - 2*p3
			if data_time[i]+time4*2<deal_time and a4==0:
				a4 = price + data_price[i] - 2*p4
				break


		data_price.append(price)
		data_time.append(deal_time)

		center_price = CenterPrice(data_price[-1000:])
		if line_num < 20:
			cp = 0
		else:
			cp = price - center_price
		# newdata = [time.mktime(deal_time.timetuple()),price,val,c1,c2,c3]
		newdata = [c1b,c2b,c3b,c4b,c1s,c2s,c3s,c4s,v1,v2,v3,v4,a1,a2,a3,a4,cp,ord_pull_gap]
		# newdata = ord_pull_gap
		# newdata = [c1b,c2b,c3b,c4b,cp]
		# print time.mktime(deal_time.timetuple())

		if deal_prev_time == deal_time:
			continue
		else:
			deal_prev_time = deal_time


		if deals == None:
			deals = newdata
		else:
			deals = np.vstack((deals, newdata))


		# print ord_pull_gap

		
	maxpoints,minpoints = Extremes(data_price)

	deals = Normalize(deals)

	# print maxpoints
	# print minpoints

	for i in maxpoints:
		color[i] = 3
		j=i
		time1 = timedelta(microseconds=100)
		while data_time[j]+time1>data_time[i] and j>0:
			j-=1
			color[j] = 2
		time1 = timedelta(seconds=1)
		while data_time[j]+time1>data_time[i] and j>0:
			j-=1
			color[j] = 1
	for i in minpoints:
		color[i] = -3
		j=i
		time1 = timedelta(microseconds=100)
		while data_time[j]+time1>data_time[i] and j>0:
			j-=1
			color[j] = -2
		time1 = timedelta(seconds=1)
		while data_time[j]+time1>data_time[i] and j>0:
			j-=1
			color[j] = -1

	A = pca(deals)
	# A = deals
	i = 0
	for r in A:
		if color[i]!=0:
			print "%.04f\t%.04f\t%d" % (r[0], r[1],color[i])

		if r[0]< -1800:
			print deals[i-1],deals[i],deals[i+1]
		# print "%.04f" % (r[0])
		i+=1
		# print [deal_time,price,val,c1,c2,c3]

	of.close()
	df.close()


if __name__ == '__main__':
	main()
