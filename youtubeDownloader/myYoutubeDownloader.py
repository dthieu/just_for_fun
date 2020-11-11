# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 00:32:42 2020

@author: Hieu Dang
"""
from tkinter import ttk
from tkinter import *
from pytube import YouTube
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
            command=lambda: Thread(target=self.getSolution).start())
        
        self.lbl_selectSolution = Label(win, text="Select solution:")
        self.cbx_chooseSolution = ttk.Combobox(win, 
                                               values=['360p'], 
                                               state="readonly", 
                                               width=7)
        self.cb_best_res        = Checkbutton(win, text="Best video quality")
        self.lbl_save           = Label(win, text="Save to: ")
        self.txt_save           = Entry(win, width=60)
        self.btn_save           = Button(win, 
                                         text="Select", 
                                         command=self.select_location)
        self.btn_download       = Button(win, 
                                         text="-> Download <-", 
                                         command=lambda: Thread(target=self.ok).start())
        self.btn_quit           = Button(win, 
                                         text='Quit', 
                                         command=lambda: win.destroy())
        self.pgsbar_progress    = ttk.Progressbar(win,
                                                  length=360, 
                                                  style='text.Horizontal.TProgressbar')
        self.lbl_progressInfo   = Label(win, text="Progress") 
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
        self.txt_save.insert(END, "D:/")
        
        # List stream
        self.scrbar = Scrollbar(win)
        self.scrbar.pack(side="right", fill="y")
        self.lstbox_streams = Listbox(win, width=80, height=20)
        self.lstbox_streams.configure(yscrollcommand=self.scrbar.set)
        self.scrbar.config(command=self.lstbox_streams.yview)
        
        # Menu bar
        self.menubar    = Menu(win)
        
        self.file       = Menu(self.menubar, tearoff=0)
        self.file.add_command(label="Open", underline=0)  
        self.file.add_command(label="Save", underline=0)
        self.file.add_separator()  
        self.file.add_command(label="Exit", underline=0, command=lambda : win.destroy())  
        self.menubar.add_cascade(label="File", underline=0, menu=self.file)
        
        self.help = Menu(self.menubar, tearoff=0)  
        self.help.add_command(label="About", underline=0, command=self.about)  
        self.menubar.add_cascade(label="Help", underline=0, menu=self.help)  
        
        win.config(menu=self.menubar)
        
        # set position
        self.lbl_link.place(x=50, y=50)
        self.txt_link.place(x=150, y=50)
        self.btn_getSolution.place(x=520, y=44)
        self.lbl_selectSolution.place(x=50, y=80)
        self.cbx_chooseSolution.place(x=150, y=80)
        self.cb_best_res.place(x=230, y=80)
        self.lbl_save.place(x=50, y=110)
        self.txt_save.place(x=150, y=110)
        self.btn_save.place(x=520, y=105)
        self.btn_download.place(x=200, y=140)
        self.btn_quit.place(x=300, y=140)
        self.lbl_progressInfo.place(x=90, y=200)
        self.pgsbar_progress.place(x=150, y=200)
        self.lstbox_streams.place(x=50, y=250)
        
    def select_location(self):
        folder_selected = filedialog.askdirectory()
        self.txt_save.delete(0, END)
        self.txt_save.insert(END, str(folder_selected)+"/")
    
    def getSolution(self):
        # Check link
        if str(self.txt_link.get()) == "":
            messagebox.showinfo("Empty link", "Input your link first!")
        self.cbx_chooseSolution['value'] += ("720p", "1080p")
        
        mystream = YouTube(self.txt_link.get()).streams
        
        for stream in mystream:
            self.lstbox_streams.insert(END, str(stream)[1:-2])
        
    
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
        if self.txt_link.get() == "":
            messagebox.showinfo("Empty link", "Input your link first!")
        
        _url  = self.txt_link.get()
        _res  = self.cbx_chooseSolution.get()
        _save = self.txt_save.get()
        
        try:
            video = YouTube(_url)
            video.register_on_complete_callback(self.on_done)
            video.register_on_progress_callback(self.on_progress)
            if self.cb_best_res.get(): # Checked
                video.streams.first().download(_save)
            else:
                video.streams.filter(res=_res, file_extension='mp4').first().download(_save)
        except:
            messagebox.showinfo("Download error", "Please check your internet connection and try again!")
    
    def about(self):
        messagebox.showinfo("About", "Purpose: download videos from Youtube and more...\n\
                            - Version: 1.0\n\
                            - Language: Python\n\
                            - Framework: Tkinter, Pytube, MoviePy\n\
                            - Dev: Hieu Dang\n\
                            --- Have a nice day! ^_^ ---")

window = Tk()
mywin = myWin(window)
window.title("Dowload video on Youtube")
# icon = PhotoImage(file="icon.png")
# window.iconphoto(False, icon)
window.geometry('630x600')
window.mainloop()







