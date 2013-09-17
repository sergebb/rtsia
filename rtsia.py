#!/usr/bin/python

import wx
import numpy as np
import scipy as sp
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


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
        bSizer2.Add(self.m_spin1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_text2 = wx.StaticText(self, wx.ID_ANY, u"Filter end:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_text2.Wrap(-1)
        bSizer2.Add(self.m_text2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spin2 = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                   wx.SP_ARROW_KEYS, 0, 10, 0)
        bSizer2.Add(self.m_spin2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

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

    def OnOpen(self,event):
        self.dirname = ''
        self.data = []
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            with open(dlg.GetPath(),"r") as f:
                for line in f:
                    items = line.split()
                    if len(items) < 4 or items[4].replace('.','',1).isdigit() == False:
                        continue
                    self.data.append(float(items[4]))
        dlg.Destroy()
        self.m_spin1.SetRange(0,len(self.data))
        self.m_spin2.SetRange(0,len(self.data))
        self.Draw(self.data)

    def Draw(self,data):
        self.fig.clf()
        self.axes = self.fig.add_axes([0.1, 0.1, 0.8, 0.8]) #size of axes to match size of figure
        idx = np.arange(len(data))
        self.axes.plot( idx,data )
        (maxp,minp) = self.Extremes(data)
        maxsub = self.GetSub(data,maxp)
        self.axes.plot( maxp,maxsub,'ro' )
        minsub = self.GetSub(data,minp)
        self.axes.plot( minp,minsub,'go' )
        self.canvas.draw()

    def OnUpdate(self, event):
        limit1 = self.m_spin1.GetValue()
        limit2 = self.m_spin2.GetValue()
        fftdata = np.fft.fft(self.data)
        if limit2 > limit1:
            for i in range(limit1,limit2):
                fftdata[i] = 0

        fildata = np.fft.ifft(fftdata)

        self.Draw(fildata)


    def Extremes(self,data,diff):
        minpoints = []
        maxpoints = []
        diff = 0.2
        lastmax = lastmin = 1
        lookMax = True
        for i in range(1,len(data)-1):
            if data[i] > data[i-1] and data[i] >= data[i+1] and lookMax == True:
                maxpoints.append(i)
                lookMax = False
            if data[i] < data[i-1] and data[i] <= data[i+1] and lookMax == False:
                minpoints.append(i)
                lookMax = True

        l = min(len(maxpoints)-1,len(minpoints)-1)
        i = 1
        if maxpoints[0]>minpoints[0]:
            while i < l:
                if diff > abs(data[maxpoints[i]] - data[minpoints[i]]):
                    maxpoints.pop(i)
                    minpoints.pop(i)
                    l-=1
                elif diff > abs(data[maxpoints[i]] - data[minpoints[i+1]]):
                    maxpoints.pop(i)
                    minpoints.pop(i+1)
                    l-=1
                else:
                    i+=1
        else:
            while i < l:
                if diff > abs(data[maxpoints[i]] - data[minpoints[i]]):
                    maxpoints.pop(i)
                    minpoints.pop(i)
                    l-=1
                if diff > abs(data[maxpoints[i+1]] - data[minpoints[i]]):
                    maxpoints.pop(i+1)
                    minpoints.pop(i)
                    l-=1
                else:
                    i+=1

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