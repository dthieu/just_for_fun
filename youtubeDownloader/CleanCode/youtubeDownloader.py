# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 00:32:42 2020

@author: Hieu Dang
"""
import tkinter as     tk
from   tkinter import ttk
from   tkinter import filedialog, messagebox
from pytube import YouTube
from threading import Thread
from PIL import ImageTk, Image # image for thumbnail 
from time import sleep
from datetime import datetime as dt
import re
from datetime import timedelta
import os
from random import randint
from moviepy.editor import VideoFileClip # convert video to mp3

beautiful_words = [
    "Don’t cry because it’s over, smile because it happened. ― Dr. Seuss",
    "You only live once, but if you do it right, once is enough. ― Mae West",
    "To live is the rarest thing in the world. Most people exist, that is all. ― Oscar Wilde",
    "It does not do to dwell on dreams and forget to live. ― J.K. Rowling",
    "Good friends, good books, and a sleepy conscience: this is the ideal life. ― Mark Twain",
    "Sometimes the questions are complicated and the answers are simple. ― Dr. Seuss",
    ""
]

class MyMenu():
    menu_items = None
    lbl_status = None
    
    def __init__(self, root):
        self.root = root
    '''
        'File- &New/Ctrl+N/self.new_file, sep, &Open/Ctrl+O/self.open_file'
    '''
    def build_menu(self, menu_definitions):
        menu_bar = tk.Menu(self.root)
        for definition in menu_definitions:
            menu = tk.Menu(menu_bar, tearoff=0)
            top_level_menu, pull_down_menus = definition.split('-')
            menu_items = map(str.strip, pull_down_menus.split(','))
            for item in menu_items:
                self._add_menu_command(menu, item)
            menu_bar.add_cascade(label=top_level_menu, menu=menu)
        self.root.config(menu=menu_bar)
    def build_status_bar(self):
        self.lbl_status = tk.Label(self.root, \
            text="Wellcome to my Youtube downloader application!")
        self.lbl_status.pack(side=tk.BOTTOM, anchor=tk.W)              
    def _add_menu_command(self, menu, item):
        if item == 'sep':
            menu.add_separator()
        else:
            menu_label, accelerator_key, cmd_callback = item.split('/')
            try:
                underline = menu_label.index('&')
                menu_label = menu_label.replace('&', '', 1)
            except ValueError:
                underline = None
            menu.add_command(label=menu_label, underline=underline, \
                             accelerator=accelerator_key, command=eval(cmd_callback))

class TabDownload(tk.Frame):

    thumbnail_img       = None
    thumbnail_w         = 256
    thumbnail_h         = 144
    file_size           = 0   # Size of download file
    my_yt               = None
    list_streams_video  = [] # video stream only
    my_stream           = None
    file_path           = ""
    file_name           = None
    my_subtitle         = None
    # Color
    btn_bg_color       = '#3b5998'
    btn_fg_color       = 'white'
    
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.create_gui()
        self.bind_func()
    
    def create_gui(self):
        self.lbl_link         = tk.Label(self, text="Link: ")
        self.txt_link         = tk.Entry(self, width=50)
        self.btn_load_stream  = tk.Button(self, text="Load stream", \
                                         bg=TabDownload.btn_bg_color, fg=TabDownload.btn_fg_color)
        self.lbl_save         = tk.Label(self, text="Save: ")
        self.txt_save         = tk.Entry(self, width=50)
        self.btn_save_to      = tk.Button(self, bg=TabDownload.btn_bg_color, \
                                         fg=TabDownload.btn_fg_color, text="Browser...")
        self.btn_download     = tk.Button(self, text="Dowload", \
                                         bg=TabDownload.btn_bg_color, fg=TabDownload.btn_fg_color)
        self.btn_cancel       = tk.Button(self, text="Cancel", \
                                         bg=TabDownload.btn_bg_color, fg=TabDownload.btn_fg_color)
        self.lbl_progress     = tk.Label(self, text="Progress:")
        self.pgsbar_progress  = ttk.Progressbar(self, length=300, style='text.Horizontal.TProgressbar')
        self.lbl_progressInfo = tk.Label(self, text="Progress") 
        self.pgsbar_progress['maximum'] = 100
        self.style = ttk.Style(self)
        self.style.layout('text.Horizontal.TProgressbar',
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}),
              ('Horizontal.Progressbar.label', {'sticky': ''})])
              # , lightcolor=None, bordercolo=None, darkcolor=None
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')
        self.lbl_list_stream = tk.Label(self, text="List streams:")
        self.lstbox_streams  = tk.Listbox(self, width=80, height=10)
        self.create_scroll_bar()
        self.cv_thumbnail    = tk.Canvas(self, width=TabDownload.thumbnail_w, \
                                               height=TabDownload.thumbnail_h, bg='black')
        self.cv_thumbnail.create_text(TabDownload.thumbnail_w//2, TabDownload.thumbnail_h//2, fill="white", \
                                        font="Arial 10 italic", \
                                        text="Thumbnail review")
        self.lbl_vidtitle        = tk.Label(self, text="Title:")
        self.lbl_vidduration     = tk.Label(self, text="Duration:")
        self.lblframe_option     = ttk.LabelFrame(self, text='Option')
        self.chk_var_convert_mp3 = tk.IntVar()
        self.ckb_convert_to_mp3  = tk.Checkbutton(self.lblframe_option, text="Convert to mp3",
                                                  variable=self.chk_var_convert_mp3)
        self.lbl_audio_name      = tk.Label(self.lblframe_option, text="File name:")
        self.txt_audio_name      = tk.Entry(self.lblframe_option, width=15)
        self.btn_get_vidsub      = tk.Button(self, text="Download video subtitle", \
                                             bg=TabDownload.btn_bg_color, fg=TabDownload.btn_fg_color)
        self.lbl_rename_videofile= tk.Label(self.lblframe_option, text="Rename video file:")
        self.txt_rename_videofile= tk.Entry(self.lblframe_option, width=15)
        # Grid widgets
        self.lbl_link.grid(       row=0, column=0, sticky='w', padx=5, pady=3)
        self.txt_link.grid(       row=0, column=1, sticky='w', padx=5, pady=3)
        self.btn_load_stream.grid(row=0, column=2, sticky='w', padx=5, pady=3)
        self.lbl_save.grid(       row=1, column=0, sticky='w', padx=5, pady=3)
        self.txt_save.grid(       row=1, column=1, sticky='w', padx=5, pady=3)  
        self.btn_save_to.grid(    row=1, column=2, sticky='w', padx=5, pady=3)
        self.btn_download.grid(   row=2, column=1, sticky='w', padx=5, pady=3)
        self.btn_cancel.grid(     row=2, column=2, sticky='w', padx=5, pady=3)
        self.lbl_progress.grid(   row=3, column=0, sticky='w', padx=5, pady=3)
        self.pgsbar_progress.grid(row=3, column=1, sticky='w', padx=5, pady=3)
        self.lbl_list_stream.grid(row=4, column=0, sticky='w', padx=2, pady=2)
        self.lstbox_streams.grid( row=5, column=0, rowspan=4, columnspan=3, sticky='w', padx=2, pady=2)
        self.cv_thumbnail.grid(   row=0, column=4, rowspan=4, sticky='w', padx=10, pady=3)
        self.lbl_vidtitle.grid(   row=4, column=4, sticky='w', padx=10, pady=2)
        self.lbl_vidduration.grid(row=5, column=4, sticky='nw', padx=10, pady=2)
        self.lblframe_option.grid(row=6, column=4, sticky='nw', padx=10, pady=2)
        self.btn_get_vidsub.grid(row=2, column=1, padx=5, pady=3)
        # Grid in option label frame
        self.lbl_rename_videofile.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.txt_rename_videofile.grid(row=0, column=1, sticky="w", padx=2, pady=2)
        self.ckb_convert_to_mp3.grid(row=1, padx=2, pady=2, sticky="w")
        self.lbl_audio_name.grid(row=2, column=0, sticky="w", padx=2, pady=2)
        self.txt_audio_name.grid(row=2, column=1, sticky="e", padx=2, pady=2)
        
        # Init value
        # self.txt_link.insert(tk.END, "https://www.youtube.com/watch?v=Z_yFB8wJSWA") # For debug
        self.txt_link.insert(tk.END, "https://www.youtube.com/watch?v=vp-Lk0bSppM") # For debug
        self.txt_save.insert(tk.END, os.path.join(os.path.expanduser('~'), "Downloads\Video"))
        self.txt_audio_name.insert(tk.END, "Untitle.mp3")
        
    def bind_func(self):
        self.btn_load_stream.bind("<ButtonRelease-1>", func=lambda event: Thread(target=self.load_stream).start())
        self.btn_save_to.bind("<ButtonRelease-1>", func=self.select_location)
        self.btn_download.bind("<ButtonRelease-1>", func=lambda event: Thread(target=self.download_stream).start())
        self.btn_cancel.bind("<ButtonRelease-1>", func=self.cancel)
        self.btn_get_vidsub.bind("<ButtonRelease-1>", func=lambda event: Thread(target=self.download_sub).start())
        
    def create_scroll_bar(self):
        x_scroll = tk.Scrollbar(self, orient="horizontal")
        # x_scroll.pack(side="bottom", fill="x")
        x_scroll.grid(row=9, column=0, columnspan=4, sticky='we')
        x_scroll.config(command=self.lstbox_streams.xview)
        y_scroll = tk.Scrollbar(self, orient="vertical")
        # y_scroll.pack(side="right", fill="y")
        y_scroll.grid(row=5, column=3, rowspan=4, sticky='ns')
        y_scroll.config(command=self.lstbox_streams.yview)
        self.lstbox_streams.config(
            xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
    
    def download_sub(self, event=None):
        if TabDownload.my_yt:
            try:
                # Get sub
                TabDownload.my_subtitle = TabDownload.my_yt.captions.get_by_language_code('en')
                sub       = TabDownload.my_subtitle.generate_srt_captions()
                save_path = self.txt_save.get()
                filename  = TabDownload.my_yt.title + ".srt"
                
                # Write sub into file
                file = open(os.path.join(save_path, filename), mode='a')
                file.write(sub)
                file.close()
                messagebox.showinfo("Done", "Download english sub successfully!")
            except:
                messagebox.showerror("Error", "There is no english sub!")
                return
        else:
            messagebox.showerror("Error", "Please load stream first and try again!")
            return
            
    def select_location(self, event=None):
        folder_selected = filedialog.askdirectory()
        self.txt_save.delete(0, tk.END)
        self.txt_save.insert(tk.END, str(folder_selected)+"/")

    def load_thumbnail(self, link, filename):
        # In order to fetch the image online
        try:
            import urllib.request as url
        except ImportError:
            import urllib as url
        try:
            url.urlretrieve(link, filename)
        except:
            messagebox.showinfo("Error", message="Cannot load thumbnail!")
    
    def cancel(self, event=None):
        TabDownload.list_streams_video  = []
        TabDownload.my_yt               = None
        TabDownload.my_stream           = None
        TabDownload.file_name           = None
        TabDownload.my_subtitle         = None
        
        self.txt_link.delete(0, tk.END)
        self.lstbox_streams.delete(0, tk.END)
        self.lbl_vidtitle.config(text="Title:")
        self.lbl_vidduration.config(text="Duration:")
        self.cv_thumbnail.delete(tk.ALL)
        self.cv_thumbnail.create_text(TabDownload.thumbnail_w//2, TabDownload.thumbnail_h//2, fill="white", \
                                        font="Arial 10 italic", \
                                        text="Thumbnail review")
        self.txt_rename_videofile.delete(0, tk.END)
        self.txt_audio_name.delete(0, tk.END)
        self.ckb_convert_to_mp3.deselect()
    
    def load_stream(self, event=None):
        # Check
        if self.txt_link.get() == "":
            messagebox.showinfo("Empty link", "Input your link first!")
        if self.lstbox_streams:
            self.lstbox_streams.delete(0, tk.END) # clear all streams
        if TabDownload.list_streams_video:
            TabDownload.list_streams_video = [] # clear all streams
        self.lbl_vidtitle.config(text="Title:")
        self.lbl_vidduration.config(text="Duration:")
        self.cv_thumbnail.delete("all")
        # MyMenu.lbl_status.config(text="Loading streams. Please wait...")
        try:
            TabDownload.my_yt = YouTube(self.txt_link.get())
        except:
            messagebox.showerror("Link error", "Please check your internet connection and try again!")
            return
        # load thumbnail
        thumbnail_url = TabDownload.my_yt.thumbnail_url
        
        if thumbnail_url != "" and "http" in thumbnail_url:
            filename  = re.findall('([-\w]+\.(?:jpg|gif|png|jpeg|tiff|raw))', thumbnail_url)[0]

            # download image
            self.load_thumbnail(thumbnail_url, filename)
            # set image into canvas thumbnail
            thumbnail   = Image.open(filename)
            width_rate  = thumbnail.width / self.cv_thumbnail.winfo_width()
            height_rate = thumbnail.height / self.cv_thumbnail.winfo_height()
            thumbnail   = thumbnail.resize((int(thumbnail.width / width_rate), \
                                        int(thumbnail.height/ height_rate)), \
                                        Image.ANTIALIAS)
            self.thumbnail_img = ImageTk.PhotoImage(thumbnail)
            self.cv_thumbnail.create_image(self.cv_thumbnail.winfo_width()//2, \
                                       self.cv_thumbnail.winfo_height()//2, \
                                       image=self.thumbnail_img)
        self.lbl_vidtitle.config(text=f"{TabDownload.my_yt.title}")
        self.lbl_vidduration.config(text=f"Duration: {str(timedelta(seconds=TabDownload.my_yt.length))}")
        # register callback
        TabDownload.my_yt.register_on_complete_callback(self.on_done)
        TabDownload.my_yt.register_on_progress_callback(self.on_progress)
        
        TabDownload.list_streams_video = TabDownload.my_yt.streams # All streams 
        
        # Add info video/audio into stream list
        for stream in TabDownload.list_streams_video:
            self.lstbox_streams.insert(tk.END, str(stream)[1:-2])
        
        # MyMenu.lbl_status.config(text="Loaded streams successfully!")
    
    def on_progress(self, stream, chunk, bytes_remaining):
        if TabDownload.file_size == 0:
            TabDownload.file_size = bytes_remaining
        else:
            downloaded = float(TabDownload.file_size - bytes_remaining)
            percentage = int((downloaded / TabDownload.file_size) * 100.0)
            self.pgsbar_progress['value'] = percentage
            self.style.configure('text.Horizontal.TProgressbar',
                        text='{:g} %'.format(percentage))
    
    def convert_mp3(self, in_video, out_audio):
        # Check audio in selected stream
        try:
            print("Converting")
            videoclip = VideoFileClip(in_video)
            audioclip = videoclip.audio
            audioclip.write_audiofile(out_audio)
            audioclip.close()
            videoclip.close()
            messagebox.showinfo("Info", "Convert video to mp3 successfully")
        except:
            messagebox.showerror("Error", f"Cannot convert {in_video} to mp3 file")
            return
    
    def on_done(self, stream, file_path):
        messagebox.showinfo("Info", "Download completed!")
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')
        self.pgsbar_progress['value'] = 0
    
    def download_stream(self, event=None):
        # Check link
        if self.txt_link.get() == "":
            messagebox.showinfo("Empty link", "Input your link first!")
            return
        
        if not TabDownload.list_streams_video:
            messagebox.showinfo("Empty link", "Please get streams first and try again!")
            return
        
        TabDownload.file_path  = self.txt_save.get()
        TabDownload.file_name = (None, self.txt_rename_videofile.get())[self.txt_rename_videofile.get() != ""]
        try:
            TabDownload.my_stream = TabDownload.list_streams_video[self.lstbox_streams.index(tk.ANCHOR)]
        except:
            messagebox.showinfo("Error", "No video selected for download!")
            
        # Download video
        # MyMenu.lbl_status.config(text="Downloading streams. Please wait...")
        try:
            TabDownload.my_stream.download( output_path=TabDownload.file_path, \
                                            filename=TabDownload.file_name)
        except:
            messagebox.showinfo("Download error", "Please check your internet connection and try again!")
            return
        # Convert mp3
        if self.chk_var_convert_mp3.get() == 1: # Checked
            print ("convert mp3")
            if TabDownload.my_stream.includes_audio_track:
                input_video = ""
                if self.txt_rename_videofile.get() != "":
                    input_video = os.path.join(TabDownload.file_path, \
                                self.txt_rename_videofile.get() + \
                                os.path.splitext(TabDownload.my_stream.default_filename)[-1])
                else: 
                    input_video = TabDownload.my_stream.default_filename
                mp3_file    = os.path.join(self.txt_save.get(), self.txt_audio_name.get())
                if '.mp3' not in mp3_file:
                    mp3_file += ".mp3"
                print("input video=",input_video, ", mp3=", mp3_file) 
                self.convert_mp3(input_video, mp3_file)
            print ("Convert OK")
class TabHistory(tk.Frame):
    def __init__(self, notebook):
        tk.Frame.__init__(self, notebook)
        lbl_inform = tk.Label(self, text="Comming soon!")
        lbl_inform.pack(side=tk.LEFT, expand=tk.YES)

class DownLoadYoutubeApp(MyMenu):
    menu_items = (
        'File- &Open/Ctrl+O/self.open_file, &Save/Ctrl+S/self.save_file, sep, &Exit/Ctrl+E/self.exit',
        'Help- About//self.about'
    )
    win_width  = 800
    win_height = 425
    def __init__(self, root):
        self.root = root
        self.root.title("===< Youtube download app <3 >===")
        self.root.geometry(f"{self.win_width}x{self.win_height}")
        self.build_menu(self.menu_items)
        self.build_status_bar()
        self.lbl_status.config(text=beautiful_words[randint(0, len(beautiful_words)-1)])
        self.create_tab_functions()
    
    def create_tab_functions(self):    
        self.tab_manage     = ttk.Notebook(self.root)
        self.download_tab   = TabDownload(self.tab_manage)
        self.history_tab    = TabHistory(self.tab_manage)
        self.tab_manage.add(self.download_tab, text="Youtube Downloader")
        self.tab_manage.add(self.history_tab, text="Download history")
        self.tab_manage.pack(expand=1, fill="both")

    def open_file(self):
        messagebox.showinfo("Check", "Test Open func OK")
    def save_file(self):
        messagebox.showinfo("Check", "Test Save func OK")
    def exit(self):
        self.root.destroy()
    def about(self):
        messagebox.showinfo("About", "Purpose: download videos from Youtube and more...\n\
                            - Version: 1.0\n\
                            - Language: Python\n\
                            - Framework: Tkinter, Pytube, MoviePy\n\
                            - Dev: Hieu Dang\n\
                            --- Have a nice day! ^_^ ---")

if __name__ == "__main__":
    root = tk.Tk()
    app  = DownLoadYoutubeApp(root)
    root.mainloop()




















