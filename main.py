import tkinter as tk
import csv
import mysql.connector
import testbench
from testbench import CrafterLexica

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        #data managment
        self.dbconnect()
        self.craftlexica = CrafterLexica(self.db, self.cursor,'craftlexica')
        #self.craftlexica.loadTablesFromFolder('ffxiv-datamining-master/csv/', self.dataminedictionary)
        #self.craftlexica.loadTable('','testitems')
        #gui managment
        self.master = master
        self.pack()
        self.create_widgets()
        #Open data file
        #csv file objects should be opened with newline=''
        #self.cvsfile = csv.reader(open('Item.csv',newline=''))
        #self.checkDatabase()

    def create_widgets(self):
        self.readNext = tk.Button(self, text="readCVS", bg="black",fg="white",command=self.readCVS)
        self.readNext.pack(side="top")

        self.loadtable = tk.Button(self, text="loadtable", bg="black",fg="white",command=self.craftlexica.autoLoadTables)
        self.loadtable.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",command=self.master.destroy)
        self.quit.pack(side="bottom")
        

    def dbconnect(self):
        self.db = mysql.connector.connect(host='localhost',user='allen',password='')
        self.cursor = self.db.cursor()

    def checkDatabase(self):
        self.cursor.execute('show databases;')
        dbname = ('mastercrafter',)
        if dbname not in self.cursor.fetchall():
            try:
                self.cursor.execute("CREATE DATABASE {}".format(dbname[0]))
            except mysql.connector.Error as err:
                print("Failed creating database: {}".format(err))
                exit(1)

    def readCVS(self):
        print(self.cvsfile.__next__())
    def say_hi(self):
        print("hi there, everyone!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()