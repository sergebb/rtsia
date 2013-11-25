#!/usr/bin/python

import sys
import numpy as np
import scipy as sp
from scipy.stats import poisson, chisquare
from datetime import datetime
from datetime import timedelta
from itertools import izip

import matplotlib
matplotlib.use('Agg')

import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def main():
    try:
        Deals_file = sys.argv[1]
        f = open(Deals_file,'r')
        Orders_file = sys.argv[2]
        o = open(Orders_file,'r')
    except:
        sys.stderr.write('Wrong file name, /script.py file orders\n')
        return 1

    time_step = timedelta(seconds=0.1)
    price_graph = []
    bs_diff = []
    deals_buy = deals_sell = 0
    for line in f:
        items = line.split(',')
        if len(items) < 4 or items[4].replace('.','',1).isdigit() == False:
            continue
            
        date = items[2]
        deal_time = datetime.strptime(date, "%Y%m%d%H%M%S%f")
        deal_price = float(items[4])
        deal_value = int(items[5])

        if items[7][0] == 'B':
            deals_buy += 1#deal_value
        elif items[7][0] == 'S':
            deals_sell += 1#deal_value
        else:
            print "Problem"

        try:
            prev_time
        except:
            prev_time = deal_time #timedelta(seconds=(deal_time.hour*3600 + deal_time.minute*60 + deal_time.second))
            prev_time -= timedelta(microseconds = prev_time.microsecond)

        while prev_time < deal_time:
            price_graph.append(deal_price)
            bs_diff.append(deals_buy-deals_sell)
            prev_time+=time_step
            print deals_buy - deals_sell
            deals_buy = deals_sell = 0

    f.close()
    o.close()

    # for i in price_graph:
    #     print i




if __name__ == "__main__":
    main()