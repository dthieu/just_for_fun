from bs4 import BeautifulSoup
import requests as rq
import unidecode
from tkinter import filedialog
from tkinter import *

class myWin:
    def __init__(self, win):
        # items
        self.lbl_link = Label(win, text="Link: ")
        self.txt_link = Entry(win, width=60)
        self.lbl_chapter = Label(win, text="Select chapter: ")
        self.txt_from = Entry(win, width=5)
        self.lbl_fromto = Label(win, text="--->")
        self.txt_to = Entry(win, width=5)
        self.lbl_save = Label(win, text="Save to: ")
        self.txt_save = Entry(win, width=60)
        self.txt_save.insert(END, "D:/")
        self.btn_save = Button(win, text="...", command=self.select_location)
        self.btn_ok = Button(win, text="OK! ^_^")
        self.btn_ok.bind('<Button-1>', self.ok)
        self.lbl_progress = Label(win, text="Progress")
        self.txt_progress = Text(win, height=50, width=63)
        self.btn_quit = Button(win, text='Quit', command=lambda: win.destroy())
        # set position
        self.lbl_link.place(x=50, y=50)
        self.txt_link.place(x=150, y=50)
        self.lbl_chapter.place(x=50, y=90)
        self.txt_from.place(x=150, y=90)
        self.lbl_fromto.place(x=180, y=90)
        self.txt_to.place(x=208, y=90)
        self.lbl_save.place(x=50, y=130)
        self.txt_save.place(x=150, y=130)
        self.btn_save.place(x=520, y=125)
        self.btn_ok.place(x=200, y=160)
        self.btn_quit.place(x=270, y=160)
        self.lbl_progress.place(x=10, y=190)
        self.txt_progress.place(x=10, y=210)
        
    def select_location(self):
        folder_selected = filedialog.askdirectory()
        self.txt_save.delete(0, END)
        self.txt_save.insert(END, str(folder_selected)+"/")
    
    def ok(self, event):
        # Check link
        if str(self.txt_link.get()) == "":
            messagebox.showinfo("Empty link", "Input your link!")
        
        # Check input chapter    
        if str(self.txt_from.get()) == "" or str(self.txt_to.get()) == "":
            messagebox.showinfo("Empty chapter", "Input chapter. ex: 1 ---> 100")
        if int(self.txt_from.get()) > int(self.txt_to.get()):
            messagebox.showinfo("Wrong chapter", "Please check your chapter again!")
            
        for i in range(int(self.txt_from.get()), int(self.txt_to.get()) + 1):
            
            my_link = str(self.txt_link.get()) + "/chuong-" + str(i) + "\n"
            
            self.txt_progress.insert(END, my_link)
            
            try:
                page = rq.get(my_link)
            except:
                self.txt_progress.insert(END, "Error: -> " + my_link)
                continue
            data = BeautifulSoup(page.content, 'html.parser')
            
            # get chapter title 
            chap_title = data.find('div', class_='h1 mb-4 font-weight-normal nh-read__title').get_text()
            
            unaccented_string = unidecode.unidecode(chap_title) # remove tone marks
            unaccented_string = '_'.join(unaccented_string.split(" "))
            unaccented_string = str(unaccented_string).replace(":","")
            unaccented_string = unaccented_string.replace("?", "")
            file_name = str(self.txt_save.get()) + unaccented_string.replace("\n", "") + ".txt"
            
            f = open(file_name, "w", encoding="utf-8")
            f.write(chap_title + "\n")
            
            content_data = data.find('div', id='js-read__content').get_text() # content of novel's chapter
            # remove blank lines
            lines = content_data.split("\n")
            non_empty_lines = [line for line in lines if line.strip() != ""]
            string_without_empty_lines = ""
            for line in non_empty_lines:
                string_without_empty_lines += line + "\n"
            
            f.write(string_without_empty_lines)
            f.close() 
        
window = Tk()
mywin = myWin(window)
window.title("Get novel from website metruyenchu.com")
window.geometry('550x600')
window.mainloop()


























