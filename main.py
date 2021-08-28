import tkinter as tk
import csv
import mysql.connector
import testbench
from CraftLexica import CrafterLexica
from testbench import FF14_IOMASTER, TextImgParser

class Application(tk.Frame):

    widgetDict = {}
    def __init__(self, master=None):
        super().__init__(master)
        #data managment
        self.dbconnect()
        self.craftlexica = CrafterLexica(self.db, self.cursor,'craftlexica')
        #self.craftlexica.loadTablesFromFolder('ffxiv-datamining-master/csv/', self.dataminedictionary)
        #self.craftlexica.loadTable('','testitems')
        #gui managment
        self.master = master
        #self.master.config(height = 720, width = 1080)
        #self.master.pack_propagate(0)
        self.pack()
        self.create_widgets()
        # FF14 IO MASTER
        self.iomaster = FF14_IOMASTER()
        self.textImgParser = TextImgParser()

    def create_button(self,buttonname, buttontext, buttonaction=None):
        newbutton = tk.Button(self, text=buttontext, bg="black",fg="white",command=buttonaction)
        newbutton.pack(side="top")
        self.widgetDict[buttonname] = newbutton

    def create_widgets(self):
        self.create_button('loadtable','load all tables',buttonaction=self.craftlexica.autoLoadTables)
        self.create_button('getitemid','get item id',buttonaction=self.executeGetItemId)
        self.create_button('getIngredients','get item ingredients',buttonaction=self.executeGetIngredients)
        self.create_button('getBOM','get item bom',buttonaction=self.executeGetBOM)
        self.create_button('capimg','capture image',buttonaction=self.executeImgCap)

        self.commandWindow = tk.Entry(self, bg="black",fg="white")
        self.commandWindow.pack(side="top", ipadx=200,ipady=200)
        self.master.geometry("1920x1080")

        self.quit = tk.Button(self, text="QUIT", fg="red",command=self.master.destroy)
        self.quit.pack(side="bottom")

    def executeImgCap(self):
        #self.iomaster.capture_img()
        img = self.textImgParser.loadImg('craftcondition.jpg')
        print(self.textImgParser.readImgText(img))

    def executeGetBOM(self):
        recipe = self.craftlexica.getRecipeStruct(itemname=self.commandWindow.get(),recursion=True)
        print(recipe)
        print(self.craftlexica.getBOM(recipe,recursion=1,multiplier=2))


    def executeGetIngredients(self):
        #print(self.craftlexica.getRecipeStruct(itemid = 5056,recursion=True))
        print(self.craftlexica.getRecipeStruct(itemname=self.commandWindow.get(),recursion=True))

    def executeGetItemId(self):
        #queryresult = self.craftlexica.getItemId(self.commandWindow.get())
        #general use csvid csvname tseting function
        queryresult = self.craftlexica.getCrafttypeId(self.commandWindow.get())
        print(queryresult)
        queryresult = self.craftlexica.getCrafttypeName(queryresult)
        print(queryresult)


        

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