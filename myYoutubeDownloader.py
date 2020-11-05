# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 00:32:42 2020

@author: Hieu Dang
"""
# https://www.youtube.com/watch?v=R2ypCXb7Go4

import tkinter as tk
from tkinter import ttk
from tkinter import *
from pytube import YouTube 
from tkinter import messagebox, filedialog
import unidecode
import re
from threading import Thread

file_size = 0

class myWin:
    def __init__(self, win):
        # items
        self.lbl_link           = Label(win, text="Link: ")
        self.txt_link           = Entry(win, width=60)
        self.btn_getSolution    = Button(
            win, 
            text='Get Solutions', 
            command=self.getSolution)
        
        self.lbl_selectSolution = Label(win, text="Select solution:")
        self.cbx_chooseSolution = ttk.Combobox(win, values=['720p'], state="readonly", width=7)
        self.lbl_save       = Label(win, text="Save to: ")
        self.txt_save       = Entry(win, width=60)
        self.txt_save.insert(END, "D:/")
        self.btn_save       = Button(win, text="...", command=self.select_location)
        self.btn_download   = Button(win, text="-> Download <-", command=lambda: Thread(target=self.ok).start())
        # self.btn_download.bind('<Button-1>', lambda: Thread(target=self.ok).start())
        self.btn_quit = Button(win, text='Quit', command=lambda: win.destroy())
        self.pgsbar_progress = ttk.Progressbar(win, length=360, style='text.Horizontal.TProgressbar')
        self.pgsbar_progress['maximum'] = 100
        self.style = ttk.Style(win)
        self.style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
              # , lightcolor=None, bordercolo=None, darkcolor=None
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')
        
        # set position
        self.lbl_link.place(x=50, y=50)
        self.txt_link.place(x=150, y=50)
        self.btn_getSolution.place(x=520, y=44)
        self.lbl_selectSolution.place(x=50, y=90)
        self.cbx_chooseSolution.place(x=150, y=90)
        self.lbl_save.place(x=50, y=130)
        self.txt_save.place(x=150, y=130)
        self.btn_save.place(x=520, y=125)
        self.btn_download.place(x=200, y=160)
        self.btn_quit.place(x=300, y=160)
        self.pgsbar_progress.place(x=150, y=200)
        
    def select_location(self):
        folder_selected = filedialog.askdirectory()
        self.txt_save.delete(0, END)
        self.txt_save.insert(END, str(folder_selected)+"/")
    
    def getSolution(self):
        # Check link
        if str(self.txt_link.get()) == "":
            messagebox.showinfo("Empty link", "Input your link first!")
        self.cbx_chooseSolution.insert()
    
    
    def on_progress(self, stream, chunk, bytes_remaining):
        global file_size
        
        if file_size == 0:
            file_size = bytes_remaining
        else:
            downloaded = float(file_size - bytes_remaining)
            percentage = int((downloaded / file_size) * 100.0)
            self.pgsbar_progress['value'] = percentage
            self.style.configure('text.Horizontal.TProgressbar',
                        text='{:g} %'.format(percentage))
    
    def on_done(self, stream, file_path):
        messagebox.showinfo("Info", "Download completed!")
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')
        self.pgsbar_progress['value'] = 0
    
    def ok(self):
        # Check link
        # Check save location
        
        _url  = self.txt_link.get()
        _res  = self.cbx_chooseSolution.get()
        _save = self.txt_save.get()
        
        try:
            video = YouTube(_url)
            video.register_on_complete_callback(self.on_done)
            video.register_on_progress_callback(self.on_progress)
            video.streams.filter(res=_res, file_extension='mp4').first().download(_save)
        except:
            messagebox.showinfo("Download error", "Please check your internet connection and try again!")
        

window = Tk()
mywin = myWin(window)
window.title("Dowload video on Youtube")
window.geometry('630x300')
window.mainloop()





