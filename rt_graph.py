#!/usr/bin/python

import wx
import sys
import numpy as np
import scipy as sp
from scipy.stats import poisson, chisquare
from datetime import datetime
from datetime import timedelta
from itertools import izip
import time
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

DIFF = 1000

DIFF_LIMIT = 10000

N_LIMIT = 10000

DEAL="deal.cvs"
ORDER="orders.txt" 

class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"RTSI analysis", pos=wx.DefaultPosition,
                          size=wx.Size(600, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_date_start = wx.StaticText(self, wx.ID_ANY, u"Date start", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_date_start.Wrap(-1)
        bSizer1.Add(self.m_date_start, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_date_end = wx.StaticText(self, wx.ID_ANY, u"Date start", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_date_end.Wrap(-1)
        bSizer1.Add(self.m_date_end, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_panel_plot = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, (1000,400), wx.TAB_TRAVERSAL)
        bSizer1.Add(self.m_panel_plot, 1, wx.EXPAND | wx.ALL, 5)

        self.m_line = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)

        bSizer1.Add(self.m_line,0,wx.EXPAND | wx.ALL, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_text1 = wx.StaticText(self, wx.ID_ANY, u"Filter Start:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_text1.Wrap(-1)
        bSizer2.Add(self.m_text1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spin1 = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                   wx.SP_ARROW_KEYS, 0, 10, 0)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.m_spin1)
        bSizer2.Add(self.m_spin1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_text2 = wx.StaticText(self, wx.ID_ANY, u"Filter end:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_text2.Wrap(-1)
        bSizer2.Add(self.m_text2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spin2 = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                   wx.SP_ARROW_KEYS, 0, 10, 0)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.m_spin2)
        bSizer2.Add(self.m_spin2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_text3 = wx.StaticText(self, wx.ID_ANY, u"Diff threshold (tens):", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_text3.Wrap(-1)
        bSizer2.Add(self.m_text3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spin3 = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                   wx.SP_ARROW_KEYS, 0, 10, 0.1)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.m_spin3)
        bSizer2.Add(self.m_spin3, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_check_live = wx.CheckBox(self, wx.ID_ANY, u"Live Update", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_check_live.SetValue(True)
        bSizer2.Add(self.m_check_live, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer2.AddSpacer(( 0, 0), 1, wx.EXPAND|wx.ALL, 5)

        self.m_button_update = wx.Button(self, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0)
        self.Bind(wx.EVT_BUTTON, self.OnUpdate, self.m_button_update)
        bSizer2.Add(self.m_button_update, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer1.Add(bSizer2, 0, wx.ALL|wx.EXPAND, 5)

        self.m_panel_ord = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, (1000,400), wx.TAB_TRAVERSAL)
        bSizer1.Add(self.m_panel_ord, 1, wx.EXPAND | wx.ALL, 5)

        bSizer3 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_button_v1 = wx.RadioButton( self, wx.ID_ANY, u"v1", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_v1)
        bSizer3.Add( self.m_button_v1, 0, wx.ALL, 5 )

        self.m_button_v2 = wx.RadioButton( self, wx.ID_ANY, u"v2", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_v2)
        bSizer3.Add( self.m_button_v2, 0, wx.ALL, 5 )

        self.m_button_v3 = wx.RadioButton( self, wx.ID_ANY, u"v3", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_v3)
        bSizer3.Add( self.m_button_v3, 0, wx.ALL, 5 )

        self.m_button_v4 = wx.RadioButton( self, wx.ID_ANY, u"v4", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_v4)
        bSizer3.Add( self.m_button_v4, 0, wx.ALL, 5 )

        self.m_button_tot = wx.RadioButton( self, wx.ID_ANY, u"tot", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_tot)
        bSizer3.Add( self.m_button_tot, 0, wx.ALL, 5 )

        self.m_button_mean = wx.RadioButton( self, wx.ID_ANY, u"mean", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_mean)
        bSizer3.Add( self.m_button_mean, 0, wx.ALL, 5 )

        self.m_button_sigma = wx.RadioButton( self, wx.ID_ANY, u"sigma", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_sigma)
        bSizer3.Add( self.m_button_sigma, 0, wx.ALL, 5 )

        self.m_button_autocorr_mean10 = wx.RadioButton( self, wx.ID_ANY, u"autocorr mean 0-10", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_autocorr_mean10)
        bSizer3.Add( self.m_button_autocorr_mean10, 0, wx.ALL, 5 )

        self.m_button_autocorr_zero = wx.RadioButton( self, wx.ID_ANY, u"autocorr (0)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_autocorr_zero)
        bSizer3.Add( self.m_button_autocorr_zero, 0, wx.ALL, 5 )

        self.m_button_chi_sqr = wx.RadioButton( self, wx.ID_ANY, u"chi square", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_chi_sqr)
        bSizer3.Add( self.m_button_chi_sqr, 0, wx.ALL, 5 )

        self.m_button_chi_sqr_local = wx.RadioButton( self, wx.ID_ANY, u"chi square loc", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_chi_sqr_local)
        bSizer3.Add( self.m_button_chi_sqr_local, 0, wx.ALL, 5 )

        self.m_button_poiss = wx.RadioButton( self, wx.ID_ANY, u"Poisson", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_RADIOBUTTON, self.OnUpdateOrders, self.m_button_poiss)
        bSizer3.Add( self.m_button_poiss, 0, wx.ALL, 5 )

        bSizer1.Add(bSizer3, 0, wx.ALL|wx.EXPAND, 5)

        bSizer4 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_slide = wx.Slider(self, wx.ID_ANY, 0, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL)
        self.Bind(wx.EVT_SCROLL, self.OnScroll, self.m_slide)
        bSizer4.Add(self.m_slide, 1, wx.ALL|wx.EXPAND, 5)

        self.m_check_live_orders = wx.CheckBox(self, wx.ID_ANY, u"Live Update", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_check_live_orders.SetValue(True)
        bSizer4.Add(self.m_check_live_orders, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_text_slide = wx.StaticText(self, wx.ID_ANY, u"100", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_text_slide.Wrap(-1)
        bSizer4.Add(self.m_text_slide, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_button_play = wx.ToggleButton(self, wx.ID_ANY, u"Play", wx.DefaultPosition, wx.DefaultSize, 0)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnTogglePlay, self.m_button_play)
        bSizer4.Add(self.m_button_play, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_button_slide = wx.Button(self, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0)
        self.Bind(wx.EVT_BUTTON, self.OnUpdateOrders, self.m_button_slide)
        bSizer4.Add(self.m_button_slide, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)


        bSizer1.Add(bSizer4, 0, wx.ALL|wx.EXPAND, 5)

        self.SetSizerAndFit(bSizer1)
        self.Layout()
        self.m_menubar = wx.MenuBar(0)
        self.m_menu_file = wx.Menu()
        self.m_menu_open = wx.MenuItem(self.m_menu_file, wx.ID_ANY, u"Open\tAlt-O", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu_file.AppendItem(self.m_menu_open)
        self.Bind(wx.EVT_MENU, self.OnOpen, self.m_menu_open)

        self.m_menu_exit = wx.MenuItem(self.m_menu_file, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu_file.AppendItem(self.m_menu_exit)
        self.Bind(wx.EVT_MENU, self.OnClose, self.m_menu_exit)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.m_menubar.Append(self.m_menu_file, u"File")

        self.SetMenuBar(self.m_menubar)

        self.Centre(wx.BOTH)

        self.dpi = 100
        self.fig_deal = Figure((10, 4), dpi=self.dpi)
        self.canvas = FigCanvas(self.m_panel_plot, -1, self.fig_deal)
        self.fig_ord = Figure((10, 4), dpi=self.dpi)
        self.canvas_ord = FigCanvas(self.m_panel_ord, -1, self.fig_ord)

        # self.max_price = 195000
        # self.min_price = 182000

        # self.spect_buy = np.zeros(self.max_price - self.min_price+1)
        # self.spect_sell = np.zeros(self.max_price - self.min_price+1)

        self.N_lines = N_LIMIT
        self.Deal = DEAL
        self.Order = ORDER

    def __del__(self):
        pass


    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               "Do you really want to close this application?",
                               "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    def LoadOrders(self,deal_time):
        order_line_num = 0
        while True:
            ordline = self.of.readline()
            if ordline[0] == '#':
                continue

            order_line_num+=1

            self.orders_time.append( datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f") )
            # self.orders_type.append( ordline.split(',')[2] )
            # self.orders_price.append( int(ordline.split(',')[6].split('.')[0]) )
            self.orders_value.append( int(ordline.split(',')[7]) )
            self.orders_action.append( int(ordline.split(',')[5]) )

            if(datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f")>deal_time):
                self.new_lines = order_line_num
                break

    def FreeOldOrders(self,deal_time,time = None):
        if time == None:
            time = timedelta(seconds = 80)
        while True:
            if self.orders_time[0] + time < deal_time:
                self.orders_time.pop(0)
                # self.orders_type.pop(0)
                # self.orders_price.pop(0)
                self.orders_value.pop(0)
                self.orders_action.pop(0)
            else: break

    def CalcOrdersData(self,deal_time):
        time1 = timedelta(seconds=0.1)
        time2 = timedelta(seconds=5)
        time3 = timedelta(seconds=15)
        time4 = timedelta(seconds=40)
        v1 = v2 = v3 = v4 = 0.0
        num=0.0
        for i in range(len(self.orders_time)-1,0,-1):
            num += 1#self.orders_value[i]               #orders speed
            if self.orders_time[i]+time1<deal_time and v1==0:
                v1=num
                break
        #     if self.orders_time[i]+time2<deal_time and v2==0: v2=num
        #     if self.orders_time[i]+time3<deal_time and v3==0: v3=num
        #     if self.orders_time[i]+time4<deal_time and v4==0:
        #         v4=num
        #         break


        self.orders_speed_1.append(v1)
        # self.orders_speed_2.append(v2)
        # self.orders_speed_3.append(v3)
        # self.orders_speed_4.append(v4)

        # if len(self.orders_total) == 0:
        #     incr_total = 0
        # else:                                         #total orders number
        #     incr_total = self.orders_total[-1]

        # for i in range(1, self.new_lines+1):
        #     if self.orders_action[-1*i] == 1:
        #         change = 1
        #     else:
        #         change = -1
        #     incr_total += change*self.orders_value[-1*i]

        # self.orders_total.append(incr_total)

        time_gap = timedelta(seconds = 0.1)             # orders speed in last 100 steps of 0.1 second
        time_steps = 100
        time_limit = timedelta(seconds = 10)
        # v_dist = np.zeros(time_steps)
        # for k in range(time_steps):
        #     time_tot_gap = time_gap*k
        #     num = 0
        #     for i in range(len(self.orders_time) - int(np.sum(v_dist))-1,0,-1):
        #         num += 1 #self.orders_value[i]
        #         if self.orders_time[i]+time_tot_gap<deal_time:
        #             v_dist[k] = num
        #             break

        v_dist = self.orders_speed_1[-1*time_steps:]

        poisson_dist_norm = poisson(np.mean(v_dist)).pmf(np.arange(time_steps-1))
        # print v_dist_sort,poisson_dist_norm, np.arange(0,5)

        # self.poisson.append(poisson_dist_norm)
        # self.chi_sqr_local.append(np.histogram(v_dist,range(time_steps),density=True)[0])
        # print v_dist, np.histogram(v_dist,range(100))
                                                        # comparison of orders speed distribution with poisson destribution
        if len(self.orig_data)> 50:
            self.chi_sqr.append( chisquare( np.histogram(v_dist,range(time_steps),density=True)[0], poisson_dist_norm)[0] )
        else:
            self.chi_sqr.append(0)


        

    def CalcDealData(self,deal_time):
        self.ln_ratio = np.zeros(100)
        # b = [np.log(p2/p1) for (p1,p2) in izip(self.orig_data[::], self.orig_data[1::])]
        # i = len(self.orders_speed_1)
        # if i< 100:
        #     self.ln_ratio = 0
        # else:
        #     self.ln_ratio = b[i-100:i]

        if len(self.orig_data) < 100:
            self.k_mean.append(0)
            self.k_sigma.append(0)
            self.autocorr_mean.append(0)
            self.autocorr_zero.append(0)
        else:
            a = self.orig_data[-100:]
            self.ln_ratio = map((lambda x: np.log(x[0]/x[1])),izip(a[1:],a))

            ln_corr = np.correlate(self.ln_ratio, self.ln_ratio, mode='full')
            newdata = ln_corr[ln_corr.size/2:]

            self.k_mean.append(np.mean(self.ln_ratio))
            self.k_sigma.append(np.std(self.ln_ratio))
            self.autocorr_mean.append(np.mean(newdata[:10]))
            self.autocorr_zero.append(newdata[0])




    def OnOpen(self,event):

        self.df = open(self.Deal,"r")
        self.of = open(self.Order,"r")

        self.dirname = ''
        self.orig_data = []
        self.deal_time = []
        self.ord_gap = []
        self.orders_time = []
        self.orders_type = []
        self.orders_price = []
        self.orders_value = []
        self.orders_action = []

        self.orders_speed_1 = []
        self.orders_speed_2 = []
        self.orders_speed_3 = []
        self.orders_speed_4 = []
        self.orders_total = []

        self.chi_sqr = []
        self.chi_sqr_local = []
        self.poisson = []

        self.autocorr_mean = []
        self.autocorr_zero = []

        self.k_mean = []
        self.k_sigma = []

        self.ord_point = 0

        deal_prev_time = 0
        self.order_prev_len = 0

        time_min_step = timedelta(seconds=1)
        # dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN|wx.FD_FILE_MUST_EXIST)
        # if dlg.ShowModal() == wx.ID_OK:
        #     
        #     with open(dlg.GetPath(),"r") as f:
        deal_line_num = 0
        for line in self.df:
            # sys.stderr.write("%d\n"%len(self.orig_data))
            items = line.split(',')
            if len(items) < 4 or items[4].replace('.','',1).isdigit() == False:
                continue
            deal_line_num+=1
                
            date = items[2]
            deal_time = datetime.strptime(date, "%Y%m%d%H%M%S%f")
            
            if(deal_line_num==1): start_time = deal_time

            deal_price = float(items[4])

            if deal_prev_time == 0: deal_prev_time = deal_time

            if len(self.orig_data) > 0 and deal_time == deal_prev_time and deal_price == self.orig_data[-1]:
                continue
            else:
                deal_prev_time = deal_time
                self.orig_data.append(deal_price)
                self.CalcDealData(deal_time)
                self.LoadOrders(deal_time)
                self.CalcOrdersData(deal_time)
                self.FreeOldOrders(deal_time)

                if len(self.orig_data)%1000 ==0:
                    print len(self.orig_data)

                if len(self.orig_data)>self.N_lines and self.N_lines!=0:
                    break


        # dlg.Destroy()
        end_time = deal_time

        # self.SetTitle(u"RTSI analysis %s-%s"%(start_time.isoformat(),end_time.isoformat()))

        self.m_date_start.SetLabel(start_time.isoformat())
        self.m_date_end.SetLabel(end_time.isoformat())

        tot_len = len(self.orig_data)
        tot_range = tot_len/2+tot_len%2
        self.m_spin1.SetRange(0,tot_range)
        self.m_spin2.SetRange(0,tot_range)
        self.m_spin3.SetRange(0,DIFF_LIMIT)
        self.m_spin1.SetValue(tot_range)
        self.m_spin2.SetValue(tot_range)
        self.m_spin3.SetValue(DIFF)
        self.m_slide.SetRange(0,tot_len-1)
        self.ord_point = self.m_slide.GetValue()
        self.CalculateExtremes(self.orig_data)
        self.DrawDeals(self.orig_data)
        self.DrawOrders()

        self.df.close()
        self.of.close()


    def CalculateExtremes(self,data):
        diff = self.m_spin3.GetValue()/10.0
        (self.maxp,self.minp) = self.Extremes(self.orig_data,diff)


    def DrawDeals(self,data):
        self.fig_deal.clf()
        self.axes_plot = self.fig_deal.add_axes([0.1, 0.1, 0.8, 0.8]) #size of axes to match size of figure
        idx = np.arange(len(self.orig_data))
        self.axes_plot.plot( idx,self.orig_data )
        # self.axes_plot.plot( idx,data )
        # self.axes_plot.plot( idx,self.ord_gap )

        maxsub = self.ExtractValues(self.orig_data,self.maxp)
        self.axes_plot.plot( self.maxp,maxsub,'ro' )
        minsub = self.ExtractValues(self.orig_data,self.minp)
        self.axes_plot.plot( self.minp,minsub,'go' )
        self.axes_plot.plot( self.ord_point,self.orig_data[self.ord_point],'yo' )
        self.canvas.draw()

    def DrawOrders(self):
        # spect_buy_tmp = np.zeros(self.max_price - self.min_price+1)
        # spect_sell_tmp = np.zeros(self.max_price - self.min_price+1)

        # for i in range(0, len(self.orders_price)):
        #     if self.orders_price[i] > self.max_price or self.orders_price[i] < self.min_price:
        #         continue 
        #     if self.orders_time[i] > deal_time_stop:
        #         break
        #     if self.orders_action[i] == 1:
        #         change = 1
        #     else:
        #         change = -1
        #     if self.orders_type[i] == 'B':
        #         spect_buy_tmp[self.orders_price[i] - self.min_price]+=change*self.orders_value[i]
        #     elif self.orders_type[i] == 'S':
        #         spect_sell_tmp[self.orders_price[i] - self.min_price]+=change*self.orders_value[i]
        maxvalue = 0
        minvalue = 0
        self.fig_ord.clf()
        self.axes = self.fig_ord.add_axes([0.1, 0.1, 0.8, 0.8]) #size of axes to match size of figure
        idx = np.arange(len(self.k_mean))
        if self.m_button_v1.GetValue():
            self.axes.plot( idx,self.orders_speed_1 )
        elif self.m_button_v2.GetValue():
            self.axes.plot( idx,self.orders_speed_2 )
        elif self.m_button_v3.GetValue():
            self.axes.plot( idx,self.orders_speed_3 )
        elif self.m_button_v4.GetValue():
            self.axes.plot( idx,self.orders_speed_4 )
        elif self.m_button_tot.GetValue():
            self.axes.plot( idx,self.orders_total )
        elif self.m_button_chi_sqr.GetValue():
            self.axes.plot( idx,np.log(self.chi_sqr) )
        elif self.m_button_chi_sqr_local.GetValue():
            idx = np.arange(len(self.chi_sqr_local[self.ord_point]))
            self.axes.plot( idx, self.chi_sqr_local[self.ord_point])
        elif self.m_button_poiss.GetValue():
            idx = np.arange(len(self.poisson[self.ord_point]))
            self.axes.plot( idx, self.poisson[self.ord_point])
        
        elif self.m_button_mean.GetValue():
            self.axes.plot( idx,self.k_mean )
        elif self.m_button_sigma.GetValue():
            self.axes.plot( idx,self.k_sigma )
        elif self.m_button_autocorr_mean10.GetValue():
            self.axes.plot( idx, self.autocorr_mean)
        elif self.m_button_autocorr_zero.GetValue():
            self.axes.plot( idx, self.autocorr_zero)

        for dot in self.maxp:
            self.axes.axvline(dot,color='r')
        for dot in self.minp:
            self.axes.axvline(dot,color='g')
        self.canvas_ord.draw()

    def OnUpdateOrders(self,event):
        if self.m_button_autocorr_zero.GetValue():
            self.m_slide.SetRange(0,99)
        else:
            tot_len = len(self.orig_data)
            self.m_slide.SetRange(0,tot_len-1)
        self.ord_point = self.m_slide.GetValue()
        self.m_text_slide.SetLabel(str(self.ord_point))

        self.DrawOrders()

    def OnTogglePlay(self,event):
        pass

    def OnScroll(self,event):
        self.ord_point = self.m_slide.GetValue()
        self.m_text_slide.SetLabel(str(self.ord_point))
        if self.m_check_live_orders.IsChecked():
            self.DrawOrders()
        if self.m_check_live.IsChecked():
            self.DrawDeals(self.orig_data)

    def OnUpdate(self, event):
        
        limit1 = self.m_spin1.GetValue()
        limit2 = self.m_spin2.GetValue()
        self.CalculateExtremes(self.orig_data)
        if limit2 > limit1:
            fftdata = np.fft.fft(self.orig_data)
            for i in range(limit1,limit2):
                fftdata[i] = 0
                fftdata[-i] = 0
            fildata = np.fft.ifft(fftdata)
            self.DrawDeals(fildata)
        else:
            self.DrawDeals(self.orig_data)
        self.DrawOrders()

    def OnSpin(self,event):
        # pass
        val1 = self.m_spin1.GetValue()
        val2 = self.m_spin2.GetValue()
        self.m_spin1.SetRange(0,val2)
        tot_len = len(self.orig_data)
        tot_range = tot_len/2+tot_len%2
        self.m_spin2.SetRange(val1,tot_range)
        if self.m_check_live.IsChecked():
            self.OnUpdate(event)


    def Extremes(self,data,diff):
        minpoints = []
        maxpoints = []
        lastmax = lastmin = 1
        lookMax = True
        lastIsMax = True
        for i in range(1,len(data)-1):
            if data[i] > data[i-1] and data[i] > data[i+1] and lookMax == True:
                lookMax = False

                if data[i] - lastmin > diff:
                    if len(maxpoints)>0 and lastIsMax == True and lastmax < data[i]:
                        maxpoints.pop()
                        maxpoints.append(i)
                        lastmax = data[i]
                        lastIsMax = True
                    elif len(maxpoints)==0 or lastIsMax == False:
                        maxpoints.append(i)
                        lastmax = data[i]
                        lastIsMax = True
            if data[i] < data[i-1] and data[i] < data[i+1] and lookMax == False:
                lookMax = True

                if lastmax - data[i] > diff:
                    if len(minpoints)>0 and lastIsMax == False and lastmin > data[i]:
                        minpoints.pop()
                        minpoints.append(i)
                        lastmin = data[i]
                        lastIsMax = False
                    elif len(minpoints)==0 or lastIsMax == True:
                        minpoints.append(i)
                        lastmin = data[i]
                        lastIsMax = False

        return maxpoints, minpoints

    def ExtractValues(self,data,idx):
        values = []
        for i in range(len(idx)):
            values.append(data[idx[i]])
        return values

def main():
    try:
        N_lines = int(sys.argv[1])
    except:
        N_lines = N_LIMIT

    try:
        Deal = sys.argv[2]
        open(Deal,"r").close()
    except:
        Deal = DEAL

    try:
        Order = sys.argv[3]
        open(Order,"r").close()
    except:
        Order = ORDER

    app = wx.App(False)
    frame = MainFrame(None)
    frame.Show()
    frame.N_lines = N_lines
    frame.Deal = Deal
    frame.Order = Order
    app.MainLoop()


if __name__ == "__main__":
    main()