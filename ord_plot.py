#! /usr/bin/python
import numpy as np
import scipy as sp
import sys
import re
from datetime import datetime
from datetime import timedelta
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

DEAL="deal.cvs"
ORDER="orders.txt" 
N = 100000
DIFF = 30
LIMIT = 30


def main():

	df = open(DEAL,"r")
	of = open(ORDER,"r")

	orders_time = []
	orders_type = []
	orders_price = []
	orders_value = []
	orders_action = []
	for ord_line in of:
		if ord_line[0] == '#':
				continue
		orders_time.append( datetime.strptime(ord_line.split(',')[3], "%Y%m%d%H%M%S%f") )
		orders_type.append( ord_line.split(',')[2] )
		orders_price.append( int(ord_line.split(',')[6].split('.')[0]) )
		orders_value.append( int(ord_line.split(',')[7]) )
		orders_action.append( int(ord_line.split(',')[5]) )

		if len(orders_price)>N and orders_action[-1] == 1:
			break

	max_price = max(orders_price)
	min_price = min(orders_price)

	spect_buy = np.zeros(max_price - min_price+1)
	spect_sell = np.zeros(max_price - min_price+1)
	print spect_sell, spect_buy
	for i in range(len(orders_price)):
		if orders_action[i] == 1:
			change = 1
		else:
			change = -1
		if orders_type[i] == 'B':
			spect_buy[orders_price[i] - min_price]+=change*orders_value[i]
		elif orders_type[i] == 'S':
			spect_sell[orders_price[i] - min_price]+=change*orders_value[i]

	idx = range(len(spect_buy))

	for i in range(len(spect_sell)):
		if spect_sell[i]>0:
			print i
			break
	for i in range(len(spect_sell)-1,0,-1):
		if spect_buy[i]>0:
			print i
			break

	imgplot = plt.plot( idx,spect_buy,'b',idx, spect_sell,'g' )
	plt.savefig('./graph.png')
	plt.clf()


if __name__ == '__main__':
	main()