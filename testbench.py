#FF14_IOMASTER dependents
import win32ui
import win32con
import win32gui
import numpy as np
from ahk import AHK
import cv2
#text reader libs dependents
import pytesseract

class FF14_IOMASTER:
    def __init__(self):
        print('ohi')
        self.ahk = AHK('C:\Program Files\AutoHotkey\AutoHotkey.exe')
        self.find_FF14()
        #monitor resolution
        self.w_resolution = 2560
        self.h_resolution = 1440

    def capture_img(self):
        cv2.imwrite('testimg.jpg',self.capture_window(self.ff14_hwnd))
        
    def find_FF14(self):
        fakevar = 0
        self.foundFF14 = False
        win32gui.EnumWindows(self.enumerateWindows, fakevar)
        if self.foundFF14 == True:
            print('FF14 FOUND!')
        
    def enumerateWindows(self, hwnd, result):
        win_text = win32gui.GetWindowText(hwnd)
        if win_text == "FINAL FANTASY XIV":
            self.foundFF14 = True
            self.ff14_hwnd = hwnd

    #very expensive function
    #from outonlimbbot
    def capture_window(self, hwnd):
        #bmpfilenamename = "out.bmp" #set this
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w_resolution, self.h_resolution)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0,0),(self.w_resolution, self.h_resolution) , dcObj, (0,0), win32con.SRCCOPY)
        #dataBitMap.SaveBitmapFile(cDC, bmpfilenamenaime)
        # faster image conversion
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h_resolution,self.w_resolution,4)
        img = img[...,:3] # remove alpha channel with num slicing
        #WARNING BIG PROBLEM MAYBE
        #img = np.ascontiguousarray(img) #solves rectangular draw problems?
        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        return img

#contains functions and tools related to screen-scraping and interpreting text
class TextImgParser:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    #def explode(self,character):
    
    def readBox(self, point1, point2, img):
        # pixel information is stored by rows (y) than columns (x)
        subimg = img[point1[1]:point2[1], point1[0]:point2[0]]
        self.readImg(subimg)

    def loadImg(self,filename):
        img = cv2.imread(filename)
        return img

    def readImgText(self,img):
        img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        cv2.imshow('readBoxKeywords',img)
        cv2.waitKey(1)
        text = pytesseract.image_to_string(img) #probably dont need deliminator anymore
        return text
 
        