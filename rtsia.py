import wx


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"RTSI analysis", pos=wx.DefaultPosition,
                          size=wx.Size(500, 300), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_panel_plot = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer1.Add(self.m_panel_plot, 1, wx.EXPAND | wx.ALL, 5)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_text1 = wx.StaticText(self, wx.ID_ANY, u"Filter Start:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_text1.Wrap(-1)
        bSizer2.Add(self.m_text1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spin1 = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                   wx.SP_ARROW_KEYS, 0, 10, 0)
        bSizer2.Add(self.m_spin1, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_text2 = wx.StaticText(self, wx.ID_ANY, u"Filter end:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_text2.Wrap(-1)
        bSizer2.Add(self.m_text2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spin2 = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                   wx.SP_ARROW_KEYS, 0, 10, 0)
        bSizer2.Add(self.m_spin2, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_check_live = wx.CheckBox(self, wx.ID_ANY, u"Live Update", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_check_live.SetValue(True)
        bSizer2.Add(self.m_check_live, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer2.AddSpacer(( 0, 0), 1, wx.EXPAND, 5)

        self.m_button_update = wx.Button(self, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer2.Add(self.m_button_update, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        bSizer1.Add(bSizer2, 0, wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.m_menubar = wx.MenuBar(0)
        self.m_menu_file = wx.Menu()
        self.m_menu_open = wx.MenuItem(self.m_menu_file, wx.ID_ANY, u"Open", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu_file.AppendItem(self.m_menu_open)
        self.Bind(wx.EVT_MENU, self.OnOpen, self.m_menu_open)

        self.m_menu_exit = wx.MenuItem(self.m_menu_file, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu_file.AppendItem(self.m_menu_exit)
        self.Bind(wx.EVT_MENU, self.OnClose, self.m_menu_exit)

        self.m_menubar.Append(self.m_menu_file, u"File")

        self.SetMenuBar(self.m_menubar)

        self.Centre(wx.BOTH)

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
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN|wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            with open(dlg.GetPath(),"r") as f:
                for line in f:
                    print line
        dlg.Destroy()


def main():
    app = wx.App(False)
    frame = MainFrame(None).Show()
    app.MainLoop()


if __name__ == "__main__":
    main()