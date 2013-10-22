#!/usr/bin/python

import wx
import sys
import numpy as np
import scipy as sp
from datetime import datetime
from datetime import timedelta
import time
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar

DIFF = 1000

DIFF_LIMIT = 1000

N_LIMIT = 1000

DEAL="deal.cvs"
ORDER="orders.txt" 

class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"RTSI analysis", pos=wx.DefaultPosition,
                          size=wx.Size(600, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_panel_plot = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, (1200,600), wx.TAB_TRAVERSAL)
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

        self.dpi = 96
        self.fig = Figure((12.4, 6.2), dpi=self.dpi)
        self.canvas = FigCanvas(self.m_panel_plot, -1, self.fig)


        self.df = open(DEAL,"r")
        self.of = open(ORDER,"r")


        self.max_price = 207925
        self.min_price = 168075

        self.spect_buy = np.zeros(self.max_price - self.min_price+1)
        self.spect_sell = np.zeros(self.max_price - self.min_price+1)

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
        while True:
            ordline = self.of.readline()
            if ordline[0] == '#':
                continue
            self.orders_time.append( datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f") )
            self.orders_type.append( ordline.split(',')[2] )
            self.orders_price.append( int(ordline.split(',')[6].split('.')[0]) )
            self.orders_value.append( int(ordline.split(',')[7]) )
            self.orders_action.append( int(ordline.split(',')[5]) )

        #     if self.orders_action[-1] == 1:
        #         change_val = 1*self.orders_value[-1]
        #     else:
        #         change_val = -1*self.orders_value[-1]

        #     if ordline.split(',')[2] == 'B':
        #         ord_time_buy = datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f")
        #         self.order_time_buy.append(ord_time_buy)
        #         self.ord_values_buy.append(int(ordline.split(',')[7]))

        #         if(ord_time_buy>deal_time):
        #             break
        #     elif ordline.split(',')[2] == 'S':
        #         ord_time_sell = datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f")
        #         self.order_time_sell.append(ord_time_sell)
        #         self.ord_values_sell.append(int(ordline.split(',')[7]))

            if(datetime.strptime(ordline.split(',')[3], "%Y%m%d%H%M%S%f")>deal_time):
                break

        # time_empty = timedelta(seconds = 30)
        # while True:
        #     if self.order_time_buy[0] + time_empty < deal_time:
        #         self.order_time_buy.pop(0)
        #         self.ord_values_buy.pop(0)
        #     else: break
        # while True:
        #     if self.order_time_sell[0] + time_empty < deal_time:
        #         self.order_time_sell.pop(0)
        #         self.ord_values_sell.pop(0)
        #     else: break

        for i in range(self.order_prev_len, len(self.orders_price)):
            if self.orders_action[i] == 1:
                change = 1
            else:
                change = -1
            if self.orders_type[i] == 'B':
                self.spect_buy[self.orders_price[i] - self.min_price]+=change*self.orders_value[i]
            elif self.orders_type[i] == 'S':
                self.spect_sell[self.orders_price[i] - self.min_price]+=change*self.orders_value[i]

        self.order_prev_len = len(self.orders_price) #used on next step

        ord_sell_min = 0
        ord_buy_max = 0

        for i in range(len(self.spect_sell)):
            if self.spect_sell[i]>0:
                ord_sell_min = i
                break
        for i in range(len(self.spect_sell)-1,0,-1):
            if self.spect_buy[i]>0:
                ord_buy_max = i
                break
        self.ord_gap.append(ord_sell_min - ord_buy_max)

    def OnOpen(self,event):
        self.dirname = ''
        self.orig_data = []
        self.ord_gap = []
        self.orders_time = []
        self.orders_type = []
        self.orders_price = []
        self.orders_value = []
        self.orders_action = []
        self.order_time_buy = []
        self.ord_values_buy = []
        self.order_time_sell = []
        self.ord_values_sell = []

        deal_prev_time = 0
        self.order_prev_len = 0
        # dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN|wx.FD_FILE_MUST_EXIST)
        # if dlg.ShowModal() == wx.ID_OK:
        #     
        #     with open(dlg.GetPath(),"r") as f:

        for line in self.df:
            sys.stderr.write("%d\n"%len(self.orig_data))
            items = line.split(',')
            if len(items) < 4 or items[4].replace('.','',1).isdigit() == False:
                continue
                
            date = items[2]
            deal_time = datetime.strptime(date, "%Y%m%d%H%M%S%f")
            if deal_prev_time == 0:
                deal_prev_time = deal_time

            if deal_prev_time == deal_time:
                continue
            else:
                deal_prev_time = deal_time
                self.orig_data.append(float(items[4]))
                self.LoadOrders(deal_time)

                if len(self.orig_data)>N_LIMIT and N_LIMIT!=0:
                    break

        # dlg.Destroy()
        tot_len = len(self.orig_data)
        tot_range = tot_len/2+tot_len%2
        self.m_spin1.SetRange(0,tot_range)
        self.m_spin2.SetRange(0,tot_range)
        self.m_spin3.SetRange(0,DIFF_LIMIT)
        self.m_spin1.SetValue(tot_range)
        self.m_spin2.SetValue(tot_range)
        self.m_spin3.SetValue(DIFF)
        self.Draw(self.orig_data)

    def Draw(self,data):
        self.fig.clf()
        self.axes = self.fig.add_axes([0.1, 0.1, 0.8, 0.8]) #size of axes to match size of figure
        idx = np.arange(len(self.ord_gap))
        # self.axes.plot( idx,self.orig_data )
        # self.axes.plot( idx,data )
        self.axes.plot( idx,self.ord_gap )
        diff = self.m_spin3.GetValue()/10.0
        (maxp,minp) = self.Extremes(self.orig_data,diff)
        maxsub = self.GetSub(self.ord_gap,maxp)
        self.axes.plot( maxp,maxsub,'ro' )
        minsub = self.GetSub(self.ord_gap,minp)
        self.axes.plot( minp,minsub,'go' )
        self.canvas.draw()

    def OnUpdate(self, event):
        limit1 = self.m_spin1.GetValue()
        limit2 = self.m_spin2.GetValue()
        if limit2 > limit1:
            fftdata = np.fft.fft(self.orig_data)
            for i in range(limit1,limit2):
                fftdata[i] = 0
                fftdata[-i] = 0
            fildata = np.fft.ifft(fftdata)
            self.Draw(fildata)
        else:
            self.Draw(self.orig_data)

    def OnSpin(self,event):
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

    def GetSub(self,data,idx):
        sub = []
        for i in range(len(idx)):
            sub.append(data[idx[i]]) 
        return sub

def main():
    app = wx.App(False)
    frame = MainFrame(None).Show()
    app.MainLoop()


if __name__ == "__main__":
    main()