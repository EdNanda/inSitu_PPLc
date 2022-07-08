# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:20:48 2020

@author: Edgar Nandayapa
"""

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from glob import glob
import time
from datetime import datetime, timedelta
import pandas as pd
import serial
import threading
from seabreeze.spectrometers import Spectrometer
import pyautogui
import sys
import os
from scipy import stats
# from scipy.optimize import curve_fit

#other libraries
# from xml_reader import xml_reader as xr


class Vacuum_GUI:


    def __init__(self):
        self.root = Tk()

        self.mic_intVar = BooleanVar(value=False)
        self.pre_intVar = BooleanVar(value=False)
        self.PLs_intVar = BooleanVar(value=False)
        # self.delay_intVar = IntVar(value=0)

        ttk.Label(self.root,text = "\n   Select available sensors\t\n").grid(row = 0, column = 0)

        mic_checkbox = ttk.Checkbutton(self.root, text = "Microscope", variable=self.mic_intVar, onvalue=True, offvalue=False)
        pre_checkbox = ttk.Checkbutton(self.root, text = "Pressure", variable=self.pre_intVar, onvalue=True, offvalue=False)
        PLs_checkbox = ttk.Checkbutton(self.root, text = "PL spectra", variable=self.PLs_intVar, onvalue=True, offvalue=False)
        # ttk.Label(self.root,text = "").grid(row = 4, column = 0)
        # ttk.Label(self.root,text = "Delay start by           seconds").grid(row = 5, column = 0,sticky = "w")
        # self.delayStart = ttk.Entry(self.root, text=self.delay_intVar, width = 3).grid(row = 5, column = 0,sticky = "e", padx = 48)

        cont_button = ttk.Button(self.root, text = "Continue",width = 10,command=self.select_sensors)



        mic_checkbox.grid(row = 1,column = 0, padx = 10, pady = 3, sticky = "nsew")
        pre_checkbox.grid(row = 2,column = 0, padx = 10, pady = 3, sticky = "nsew")
        PLs_checkbox.grid(row = 3,column = 0, padx = 10, pady = 3, sticky = "nsew")

        cont_button.grid(row = 6,column = 0, padx = 3, pady = 3, sticky = "nsew")
        # self.checkboxes.append(checkbox)


    def select_sensors(self):

        self.isMic = self.mic_intVar.get()
        self.isCam = False
        self.isPressure = self.pre_intVar.get()
        self.isSpectro = self.PLs_intVar.get()
        # self.isXML = True

        self.root.withdraw()
        self.create_widgets()


    def create_widgets(self):

        ## ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Main window setup ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        self.master = Toplevel()
        self.master.title("Vacuum chamber process")
        self.master.geometry ("1280x800+0+0") #Size of Main Window
        self.master.rowconfigure(0, weight = 1) #Resizing of Main window will resize each frame individually 1-to-1
        self.master.rowconfigure(1, weight = 1)
        self.master.columnconfigure(0, weight = 1)
        self.master.columnconfigure(1, weight = 1)
        self.master.columnconfigure(2, weight = 1)
        #master.resizable(False,False)
        #master.minsize(640,480)

        ## Configuration of Styles. They make fonts and buttons look the same
        self.style = ttk.Style()
        self.style.configure("frameST.TLabelframe", height = 400, width = 100, padding = (30,15), fill="both")
        self.style.configure("frameST2.TLabelframe", height = 400, width = 50, padding = (10,10), fill="both")
        self.style.configure("txtST.TLabel", foreground = "black", font = ("Arial", 12, "normal"))
        self.style.configure("bigST.TLabel", foreground = "black",font = ("Arial", 24, "bold"))
        self.style.configure("redST.TLabel", foreground = "red",font = ("Arial", 24, "bold"))
        self.style.configure("blueST.TLabel", foreground = "blue",font = ("Arial", 24, "bold"))
        self.style.configure("fieldST.TLabel", foreground = "black", font = ("Arial", 14, "bold"), justify = CENTER)
        self.style.configure("entryST.TEntry", font = ("Arial", 16, "normal"))
        self.style.configure("canvasST.TCanvas", bg = "white", width = 300, height = 200)
        self.style.configure("StaStoStyle.TButton", foreground = "blue", font = ("Arial", 14, "bold"),width=5)
        self.style.configure("StopStyle.TButton", background = "red", foreground = "black", font = ("Arial", 18, "bold"),width=5)
        self.style.map("StaStoStyle.TButton", foreground = [("pressed", "red")])

        ## ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Initialization of processes  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

        ### Setup cameras
        if self.isMic:
            self.cap_MIC = cv2.VideoCapture(0)
            self.current_image_MIC = None
        # if self.isCam:
        #     self.cap_CAM = cv2.VideoCapture(0)
        #     self.current_image_CAM = None
        self.fps_entry = 30  # Initializes frames-per-second

        ### Setup Spectrometer (OceanOptics Flame)
        if self.isSpectro:
            self.spec = Spectrometer.from_first_available()
            # self.spec = Spectrometer.from_serial_number(serial="FLMS15932")
            self.spec.integration_time_micros(100000)
            self.spec_waveL = self.spec.wavelengths()[2:]
            self.spec_counts = []
            # self.spec_waveL = list(range(300,900))


        ### Setup pressure sensor
        if self.isPressure:
            self.pressureSensor = serial.Serial("COM3")
            self.pressureSensor.baudrate = 9600
            self.pressureSensor.bytesize = 8
            self.pressureSensor.parity = 'N'
            self.pressureSensor.stopbits = 1
            self.pressureArray = []
            self.timeElapArray = []

        self.plot_ratio = 3/4 #For image 4:3
        ### Setup Plots
        # PLspectra plot
        self.fig_pls = Figure()#figsize=[4,3])
        self.ax1 = self.fig_pls.add_subplot(111)
        
        # Pressure plot
        self.fig_pres = Figure()#figsize=[4,3])
        self.ax2 = self.fig_pres.add_subplot(111)

        ### running process refers to saving data
        self.runningProcess = False
        self.startP = False
        self.delay = 0
        


        ## ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ Frame configurations  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

        ## - - - - - Pressure frame - - - - -
        if self.isPressure:
            self.pressure_frame = ttk.LabelFrame(self.master)
            self.pressure_frame.config(style="frameST.TLabelframe",text = "Pressure")
            self.pressure_frame.grid(row=0,column=0,columnspan=2)
            
            self.pres_label = ttk.Label(self.pressure_frame, text = "Current Pressure")
            self.rate_label = ttk.Label(self.pressure_frame, text = "Current Rate")
            self.presLive_label = ttk.Label(self.pressure_frame, text = "0.00 E-2 mbar")
            self.rateLive_label = ttk.Label(self.pressure_frame, text = "0.00 L/s")
            self.pres_image = FigureCanvasTkAgg(self.fig_pres, master=self.pressure_frame)
            
            self.pres_label.config(style = "txtST.TLabel", justify = LEFT, anchor = "sw")
            self.rate_label.config(style = "txtST.TLabel", justify = RIGHT, anchor = "se")
            self.presLive_label.config(style = "fieldST.TLabel", justify = CENTER, anchor = "sw")
            self.rateLive_label.config(style = "fieldST.TLabel", justify = CENTER, anchor = "se")
    
            self.pres_image.get_tk_widget().grid(padx = 10, row=2,column=0, columnspan=2)
            self.pres_label.grid(padx = 10, row=0,column=0)
            self.rate_label.grid(padx = 10, row=0,column=1)
            self.presLive_label.grid(padx = 30, row=1,column=0)
            self.rateLive_label.grid(padx = 30, row=1,column=1)
        
        
        ## - - - - - Microscope frame - - - - -
        if self.isMic:
            self.microscope_frame = ttk.LabelFrame(self.master)
            self.microscope_frame.config(style="frameST.TLabelframe",text = "Microscope")
            self.microscope_frame.grid(row=0,column=1,columnspan=2)
            
            framespersecond = StringVar()
            self.fps_label = ttk.Label(self.microscope_frame, text = "FPS selection")
            self.ftt_label = ttk.Label(self.microscope_frame, text = "Frames Taken")
            self.ftt_labelLive = ttk.Label(self.microscope_frame, text = "000") ##ftt=frames total
            self.fps_entry = ttk.Combobox(self.microscope_frame, textvariable = framespersecond)
            self.micro_image = Label(self.microscope_frame)
            
            self.ftt_label.config(style = "txtST.TLabel", justify = LEFT, anchor = "sw")
            self.fps_label.config(style = "txtST.TLabel", justify = RIGHT, anchor = "se")
            self.ftt_labelLive.config(style = "fieldST.TLabel", anchor = "se")
            self.fps_entry.config(width = 5, values = ("30","20","15","10","6","5","2","1"))
            self.micro_image.grid(row=0,column=0, columnspan=2)
            self.ftt_label.grid(padx = 10, row=1,column=1)
            self.fps_label.grid(padx = 10, row=1,column=0)
            self.ftt_labelLive.grid(padx = 30, row=2,column=1)
            self.fps_entry.grid(padx = 30, row=2,column=0)
        else:
            framespersecond = StringVar()
            self.fps_entry = ttk.Combobox(self.master, textvariable = framespersecond)

        
        ## - - - - - Photoluminescence (Notebook) frame - - - - -
        if self.isSpectro:
            self.PL_frame = ttk.LabelFrame(self.master)
            self.PL_frame.config(style="frameST.TLabelframe",text = "Photoluminescence")
            self.PL_frame.grid(row=1,column=0)
            self.PLNo_image = FigureCanvasTkAgg(self.fig_pls, master=self.PL_frame)
            # self.PL2dButton = BooleanVar()
            # self.PL2D_button = ttk.Checkbutton(self.PL_frame, text="2D View", variable=self.PL2dButton,
            #                               command=lambda: self.test(self.PL2dButton))
            self.PLNo_image.get_tk_widget().grid(row=0,column=0, columnspan=3)
            ttk.Label(self.PL_frame, text = "Integration Time (s)").grid(row=1,column=0, columnspan=1, sticky=E)
            self.integrationtime = StringVar()
            # self.integrationtime = 100000
            self.int_time = ttk.Entry(self.PL_frame, textvariable = self.integrationtime, width = 20,justify="right")
            # self.int_time.xview_moveto(1)
            self.int_time.insert(0,"0.1")
            self.int_time.grid(row=1,column=1, columnspan=1)
            # self.int_time.set(100000)
            self.intTimeButton = ttk.Button(self.PL_frame, text = "Set",width = 7, command=self.set_int_time).grid(row=1,column=2, sticky=W)
            # self.PL2D_button.pack(expand=True)


        # ## - - - - - Camera frame - - - - -
        # self.cam_frame = ttk.LabelFrame(self.master)
        # self.cam_frame.config(height = 200, width = 300, padding = (30,15),text = "Camera")
        # self.cam_frame.grid(row=1,column=1)
        # self.camera_image= Label(self.cam_frame)
        # self.camera_image.pack()
        # sampList = StringVar()
        # self.sample_combobox = ttk.Combobox(self.cam_frame, textvariable = sampList, width = 17)
        # self.sample_combobox.pack()
        # self.sample_combobox.config(values=("samp1","samp2","samp3"))
        # self.sample_combobox.current(0)
        # self.picture_button = ttk.Button(self.cam_frame, text = "Take Picture", width = 20, command=self.take_CameraPic).pack()

        
        ## - - - - - Config frame - - - - -
        self.config_frame = ttk.LabelFrame(self.master)
        self.config_frame.config(style="frameST2.TLabelframe",text = "Config")
        # self.config_frame.grid(row=1,column=2)
        self.config_frame.grid(row=1,column=1)

        # ttk.Button(self.config_frame, text = 'Close',command = self.close_window).grid(row=0,column=0, columnspan=2)
        self.fileLabel = ttk.Label(self.config_frame, style = "txtST.TLabel", text = "Sample Name").grid(row=1,column=0, columnspan=2)
        self.fileEntry = ttk.Entry(self.config_frame, width = 20)
        self.histButton = ttk.Button(self.config_frame, text = "History",width = 7, command=self.display_history).grid(row=2,column=1, sticky=E)
        self.fileEntry.insert(0,'Sample')
        self.fileEntry.grid(row=2,column=0, columnspan=2,sticky=W)
        # self.histButton.grid(row=4,column=0)

        if glob('C:\\Users\\LP50\\Desktop\\Edgar\\'):
            self.folder_path = 'C:\\Users\\LP50\\Desktop\\Edgar\\'
        elif glob('F:\\Seafile\\IJPrinting_Edgar-Florian\\'):
            self.folder_path = 'F:\\Seafile\\IJPrinting_Edgar-Florian\\'
        else:
            self.folder_path = 'C:\\Documents\\Data\\'

        self.folderLabel = ttk.Label(self.config_frame,style = "txtST.TLabel", text = "Folder Location").grid(row=3,column=0, columnspan=2)
        self.folderEntry = ttk.Entry(self.config_frame, width = 27)
        self.folderEntry.insert(0,self.folder_path)
        self.folderButton = ttk.Button(self.config_frame, text = "...",width = 3, command=self.browseButton).grid(row=4,column=0)
        self.folderEntry.grid(row=4,column=1)

        ttk.Label(self.config_frame, text = "\n").grid(row=5,column=0, columnspan=2)

        self.startButton = ttk.Button(self.config_frame,command = self.startProcess, text = "Start")
        self.startButton.config(style = "StaStoStyle.TButton")
        self.stopButton = ttk.Button(self.config_frame,command = self.stopProcess, text = "Stop")
        self.stopButton.config(style = "StopStyle.TButton")
        self.startButton.grid(row=6,column=0, columnspan=2)
        self.elapsedVar = StringVar()
        self.elapsedVar.set("00:00")
        self.elaptimLabel = ttk.Label(self.config_frame,style = "txtST.TLabel", text = "\nElapsed Time").grid(row=7,column=0, columnspan=2)
        self.elapsedLabel = ttk.Label(self.config_frame,style ="bigST.TLabel", textvariable = self.elapsedVar)
        self.elapsedLabel.grid(row=8,column=0, columnspan=2)



        ## - - - - - Live variables frame - - - - -
        self.LiveVar_frame = ttk.LabelFrame(self.master)
        self.LiveVar_frame.config(style="frameST2.TLabelframe",text = "Variables")
        # self.LiveVar_frame.grid(row=0,column=2)
        self.LiveVar_frame.grid(row=1,column=2)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Printer settings").grid(row=0,column=0,columnspan=4)

        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Active Nozzles").grid(row=1,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Print Speed").grid(row=2,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Quality Factor").grid(row=3,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Resolution").grid(row=4,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Printhead Temp").grid(row=1,column=2)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Substrate Temp").grid(row=2,column=2)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Voltage").grid(row=3,column=2)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Swaths").grid(row=4,column=2)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Wait Time").grid(row=5,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Total Time").grid(row=5,column=2)

        self.intVar_waitT = IntVar()
        self.intVar_totalT = IntVar()

        self.varLabel1 = ttk.Entry(self.LiveVar_frame, width = 5, style = "entryST.TEntry")
        self.varLabel2 = ttk.Entry(self.LiveVar_frame, width = 5)
        self.varLabel3 = ttk.Entry(self.LiveVar_frame, width = 5, text = "QF")
        self.varLabel4 = ttk.Entry(self.LiveVar_frame, width = 5, text = "")
        self.varLabel5 = ttk.Entry(self.LiveVar_frame, width = 5, text = "30")
        self.varLabel6 = ttk.Entry(self.LiveVar_frame, width = 5, text = "20")
        self.varLabel7 = ttk.Entry(self.LiveVar_frame, width = 5, text = "100")
        self.varLabel8 = ttk.Entry(self.LiveVar_frame, width = 5, text = "12")
        self.varLabelWT = ttk.Entry(self.LiveVar_frame, width = 5, text=self.intVar_waitT)
        self.varLabelTT = ttk.Entry(self.LiveVar_frame, width = 5, text=self.intVar_totalT)

        self.varLabel1.grid(row=1,column=1)
        self.varLabel2.grid(row=2,column=1)
        self.varLabel3.grid(row=3,column=1)
        self.varLabel4.grid(row=4,column=1)
        self.varLabel5.grid(row=1,column=3)
        self.varLabel6.grid(row=2,column=3)
        self.varLabel7.grid(row=3,column=3)
        self.varLabel8.grid(row=4,column=3)
        self.varLabelWT.grid(row=5,column=1)
        self.varLabelTT.grid(row=5,column=3)

        self.repopulate_button = ttk.Button(self.LiveVar_frame, text = u"\u2B6F", width = 3, command=self.repopulate_metafields)
        self.repopulate_button.grid(row=6,column=3, sticky=E)

        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "").grid(row=5,column=0, columnspan=4)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Ink Details").grid(row=6,column=0, columnspan=4)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Perovskite").grid(row=7,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Adds.").grid(row=7,column=2, sticky=E)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Solvents").grid(row=8,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Ratio").grid(row=8,column=2, sticky=E)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Conc.").grid(row=9,column=2, sticky=E)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Substrate").grid(row=9,column=0)

        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "").grid(row=10,column=0, columnspan=4)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Glovebox Variables").grid(row=11,column=0, columnspan=4)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Temperature").grid(row=12,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "H2O content").grid(row=13,column=0)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "O2 content").grid(row=13,column=2)
        ttk.Label(self.LiveVar_frame, style = "txtST.TLabel", text = "Comments:").grid(row=14,column=0)
        self.varEntry_Pe = ttk.Entry(self.LiveVar_frame, width = 10)
        self.varEntry_Ad = ttk.Entry(self.LiveVar_frame, width = 5)
        self.varEntry_So = ttk.Entry(self.LiveVar_frame, width = 15)
        self.varEntry_Ra = ttk.Entry(self.LiveVar_frame, width = 5)
        self.varEntry_Su = ttk.Entry(self.LiveVar_frame, width = 10)
        self.varEntry_Co = ttk.Entry(self.LiveVar_frame, width = 5)
        self.varEntry_Te = ttk.Entry(self.LiveVar_frame, width = 5)
        self.varEntry_Wa = ttk.Entry(self.LiveVar_frame, width = 5)
        self.varEntry_Ox = ttk.Entry(self.LiveVar_frame, width = 5)
        self.varEntry_cc = ttk.Entry(self.LiveVar_frame, width = 27)
        self.varEntry_Pe.grid(row=7,column=1,columnspan=2, sticky=W)
        self.varEntry_Ad.grid(row=7,column=3)
        self.varEntry_So.grid(row=8,column=1,columnspan=2, sticky=W)
        self.varEntry_Ra.grid(row=8,column=3)
        self.varEntry_Su.grid(row=9,column=1,columnspan=2, sticky=W)
        self.varEntry_Co.grid(row=9,column=3)
        self.varEntry_Te.grid(row=12,column=1)
        self.varEntry_Wa.grid(row=13,column=1)
        self.varEntry_Ox.grid(row=13,column=3)
        self.varEntry_cc.grid(row=14,column=1,columnspan=3, sticky=W)

        ## Start the program
        # self.master.bind("<Configure>", onsize)
        self.todaydate = datetime.now().strftime("%Y%m%d")
        self.datePath = self.folder_path+"\\"+self.todaydate+"\\"
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)
        self.processes_loop()

    ## ~o~o~o~o~o~o~o~o Administrative functions o~o~o~o~o~o~o~o~

    def create_date_folder(self):
        #Sample name and folder path
        # self.todaydate = datetime.now().strftime("%Y%m%d")
        # self.datePath = self.folder_path+"\\"+self.todaydate+"\\"

        # Check if date folder exists
        if not os.path.exists(self.datePath):
            os.mkdir(self.datePath)
            print("created date folder "+self.datePath)
        else:
            pass
        
    def set_int_time(self):
        # if self.integrationtime == "":
        try:
            self.integrationtime = float(self.int_time.get())
        # if isinstance(int(self.int_time.get()), int):
        #     self.integrationtime = self.int_time.get()
        # else:
        except:
            self.integrationtime = 0.1

        
        self.int_time.delete(0,END)
        self.int_time.insert(0,self.integrationtime)
        
        integration = self.integrationtime * 1000000
        
        # print(self.integrationtime)
        self.spec.integration_time_micros(integration)

    def display_history(self):
        ##Create Windows
        self.hist = Toplevel()
        # self.text_field = Text(self.hist, height = 40, width = 52) 
                
        ## Gather metadata
        file_list = glob(self.datePath+'\\*\\*metadata.csv')
        file_names = []
        files_df = []
        for p in file_list:
            file_names.append(p.rsplit("\\",2)[-2])
            df = pd.read_csv(p, index_col=0, header=0, parse_dates=True,error_bad_lines=False)
            files_df.append(df)
        dframe = pd.concat(files_df, axis=1, ignore_index=True)
        dframe.columns = file_names
        ##Fix metadata structure
        dframe = dframe.transpose()
       
        dframe["DateTime"] = pd.to_datetime(dframe["DateTime"], format="%d.%m.%Y-%H:%M:%S", errors="ignore")
        dframe.sort_values(by="DateTime", inplace=True)
        ## get relevant metadata
        cols_names = ["DateTime","Comments"]
        
        hist_text = ''
        done_count = 0
        for r, dF in enumerate(dframe.index):
            single_text = dF+"\t"
            for cn in cols_names:
                if cn =="DateTime":
                    if dframe[cn][dF] + timedelta(minutes=20) < datetime.now():
                        single_text = "**"+single_text+dframe[cn][dF].strftime('%H:%M:%S') +"\t\t"
                        done_count += 1
                    else:
                        single_text = single_text+dframe[cn][dF].strftime('%H:%M:%S') +"\t\t"
                else:
                    single_text = single_text+ str(dframe[cn][dF]) +"\t"
                
            hist_text = hist_text+single_text+"\n"
        hist_text = "%s \nSamples ready: %d/%d" %(hist_text,done_count,len(file_list))
        # print(hist_text)
        ttk.Label(self.hist, style = "txtST.TLabel", text = hist_text).grid(row=0,column=0)
        # self.text_field.insert(END, hist_text) 
                            
            

    def create_sample_folder(self, retries=1):
        self.sample_name = self.fileEntry.get()
        self.full_path = self.datePath+self.sample_name+"\\"

        # Check if there are repeated samples, if so, create dup folder
        if os.path.exists(self.full_path):
            self.full_path =self.full_path[:-1]+"_dup"+str(retries)+"\\"
            if os.path.exists(self.full_path):
                retries +=1
                self.create_sample_folder(retries)
            else:
                os.mkdir(self.full_path)
                print("created duplicated folder "+self.full_path)
        else:
            os.mkdir(self.full_path)
            print("created sample folder "+self.full_path)


    def browseButton(self):
        # Allow user to select a directory
        self.folder_path = filedialog.askdirectory()
        self.folderEntry.delete(0, 'end')
        self.folderEntry.insert(0,self.folder_path)
        return self.folder_path


    def list_measured_samples(self):
        # This is used to populate combobox from Camera frame
        all_meas_samples = []
        sample_list = glob(self.folder_path+"*")
        for sl in sample_list:
            nameholder = sl.split("\\")[-1]
            all_meas_samples.append(nameholder)
        # self.sample_combobox.config(values=all_meas_samples)


    def set_text_metavalues(self):
        # Populates fixed variables with data from xml file
        label_vars = [self.varLabel1,self.varLabel2,self.varLabel3,self.varLabel4,
                      self.varLabel5,self.varLabel6,self.varLabel7,self.varLabel8
                      ]
        label_names = ["ActiveNozzles","PrintSpeed","QualityFactor","XResolution",
                       "PrintHeadTemperature","SubstrateTemperature","AVoltage",
                       "Swaths"]

        for n,lvs in enumerate(label_vars):
            lvs["text"] = self.xml_data[label_names[n]]


    def get_entry_metavalues(self):
        ## Save input values from User, related to perovskite ink and Glovebox
        user_input_names = ["ActiveNozzles","PrintSpeed","QualityFactor","XResolution",
                            "PrintHeadTemperature","SubstrateTemperature","AVoltage","Swaths",
                            "WaitRunTime","TotalRunTime",
                           "PerovskiteType","PerovskiteSolvents","PerovskiteSolventsRatio",
                            "GloveboxTemperature(c)","GloveboxH2Ocontent(ppm)","GloveboxO2content(ppm)","Comments",
                            "Additives","Concentration","Substrate"]
        user_input_vars = [self.varLabel1,self.varLabel2,self.varLabel3,self.varLabel4,
                           self.varLabel5,self.varLabel6,self.varLabel7,self.varLabel8,
                           self.varLabelWT,self.varLabelTT,
                           self.varEntry_Pe,self.varEntry_So,self.varEntry_Ra,
                           self.varEntry_Te,self.varEntry_Wa,self.varEntry_Ox,self.varEntry_cc,
                           self.varEntry_Ad, self.varEntry_Co, self.varEntry_Su]

        for c,uin in enumerate(user_input_names):
            self.xml_data[uin] = user_input_vars[c].get()

        #add current time and date
        now = datetime.now()
        self.xml_data["DateTime"]=now.strftime("%d.%m.%Y-%H:%M:%S")

    def repopulate_metafields(self):
        todaydate = datetime.now().strftime("%Y%m%d")
        metafile = sorted(glob(self.folder_path+"\\"+todaydate+"\\*\\*metadata.csv"),key=os.path.getmtime)[-1]
        meta_df = pd.read_csv(metafile, header=None, index_col=0, squeeze=True)

        user_input_names = ["PerovskiteType","PerovskiteSolvents","PerovskiteSolventsRatio",
                            "GloveboxTemperature(c)","GloveboxH2Ocontent(ppm)","GloveboxO2content(ppm)","Comments",
                            "Additives","Concentration","Substrate",
                            "WaitRunTime","TotalRunTime",
                            "ActiveNozzles","PrintSpeed","QualityFactor","XResolution",
                            "PrintHeadTemperature","SubstrateTemperature","AVoltage",
                            "Swaths"]
        user_input_vars = [self.varEntry_Pe,self.varEntry_So,self.varEntry_Ra,
                           self.varEntry_Te,self.varEntry_Wa,self.varEntry_Ox,self.varEntry_cc,
                           self.varEntry_Ad, self.varEntry_Co, self.varEntry_Su,
                           self.varLabelWT,self.varLabelTT,
                           self.varLabel1,self.varLabel2,self.varLabel3,self.varLabel4,
                           self.varLabel5,self.varLabel6,self.varLabel7,self.varLabel8
                           ]

        for i, mdi in enumerate(user_input_names):
            user_input_vars[i].delete(0, 'end')
            user_input_vars[i].insert(0,meta_df[mdi])




    ## ~o~o~o~o~o~o~o~o Sensor functions o~o~o~o~o~o~o~o~
    def readSensor_Microscope(self,timeEla):
        state_MIC, frame_MIC_raw = self.cap_MIC.read()
        hue = cv2.cvtColor(frame_MIC_raw, cv2.COLOR_BGR2HSV)[:,:,0]
        gray_MIC = cv2.cvtColor(frame_MIC_raw, cv2.COLOR_BGR2GRAY)
        frame_MIC = cv2.cvtColor(frame_MIC_raw, cv2.COLOR_BGR2RGB)

        ## resize image from camera (removes black frame of raw data)
        y = frame_MIC.shape[0]
        x = frame_MIC.shape[1]
        d = 60
        frame_MIC = frame_MIC[d:y-d,d:x-d]
        frame_MIC = cv2.resize(frame_MIC, (0,0), fx=0.8,fy=0.8)

        hue_arr = np.asarray(hue).reshape(-1)
        hue_arr = hue_arr[hue_arr > 2]

        if state_MIC:
            self.current_image_MIC = Image.fromarray(frame_MIC)
            imgtk_MIC = ImageTk.PhotoImage(image=self.current_image_MIC)
            self.micro_image.imgtk = imgtk_MIC
            self.micro_image.config(image=imgtk_MIC)

            n_bins = 180
            self.countsGray, _ = np.histogram(gray_MIC, list(range(n_bins))) ##Useful when spectrometer working
            if self.isSpectro:
                self.countsHue, _ = np.histogram(hue_arr, list(range(n_bins)))
                # print(len(self.countsHue), self.countsHue)
            else:
                self.countsHue = self.plotting_PLmic(hue_arr)

        if self.runningProcess:
            timeEla = str(round(timeEla,2)).replace(".","o")
            self.ftt_labelLive.config(text=str(self.frame_counter))
            self.frame_counter += 1
            try:
                os.mkdir(self.full_path+"images_drying\\")
            except:
                pass
            cv2.imwrite(self.full_path+"images_drying\\"+self.sample_name+"_"+timeEla+".jpg", frame_MIC_raw)



    def readSensor_Spectrometer(self):
        if True:
            try:
                s_counts = self.spec.intensities()[2:]
                self.plotting_PLspectra(s_counts)
            except:
                s_counts=0
        else:
            s_counts= np.random.normal(size=600)
            time.sleep(1)            
            self.plotting_PLspectra(s_counts)

        return s_counts



    def readSensor_Pressure(self,timeElap):
        try:
            # pressure_value = float(self.pressureSensor.readline())
            self.pressureSensor.write(b"001M^\r") # sending measurement command
            spr = self.pressureSensor.read(12)
            p_val = float(spr[4:8])/1000
            p_exp = int(spr[8:10])-20
        
            pressure_value = p_val*10**p_exp
        except:
            pressure_value = 0

        if self.runningProcess:
            self.pressureArray.append(pressure_value)

            self.plotting_pressure()

        else:
            self.presLive_label.config(text = "{:.2f} mbar".format(pressure_value))
            

    def readSensor_Camera(self):
        cv2.cvtColor()
        state_CAM, self.frame_CAM = self.cap_CAM.read() #Get data from Camera
        
        frame_CAM_s = cv2.cvtColor(self.frame_CAM, cv2.COLOR_BGR2RGB) #Convert color scheme
        frame_CAM_s = cv2.resize(frame_CAM_s, (0,0), fx=0.3,fy=0.3) #Resize image

        if state_CAM: ##Should be in GUI part, send frame_CAM
            self.current_image_CAM = Image.fromarray(frame_CAM_s)
            imgtk_CAM = ImageTk.PhotoImage(image=self.current_image_CAM)
            self.camera_image.imgtk = imgtk_CAM
            self.camera_image.config(image=imgtk_CAM)

    def take_CameraPic(self):
        #self.folder_path
        try:
            sample_name = self.sample_combobox.get()
        except:
            sample_name = self.fileEntry.get()

        cv2.imwrite(self.folder_path+sample_name+"\\"+sample_name+"_full_picture.jpg", self.frame_CAM)




    ## ~o~o~o~o~o~o~o~o plotting functions o~o~o~o~o~o~o~o~


    def plotting_pressure(self): ## Triggered by sensor
        # Imported values to plot
        x_time = self.timeElapArray
        y_pres = self.pressureArray

        # Setting the graph appearance
        ##This should be in GUI, send x_time and y_pres
        self.ax2.clear()
        self.ax2.set_ylabel("Pressure (mbar)", fontsize=12)
        self.ax2.set_xlabel("Time (sec)", fontsize=12)
        self.ax2.grid()
        self.ax2.set_yscale('log')

        # Plot data
        self.ax2.scatter(x_time,y_pres)
        # self.ax2.set_aspect(1.0/self.ax2.get_data_ratio()*self.plot_ratio)


        # Calculate pumping rate
        chamber_volume = 0.25 #Vacuum chamber volume
        try:
            y_max=1000 #or max(y_pres)
            y_min=min(y_pres)
            t_max = x_time[y_pres.index(y_min)]##This might return an array, fix it
        except:
            y_max=0
            y_min=0
            t_max = 0

        try:
            rate = chamber_volume/t_max*np.log(y_max/y_min)#
        except:
            rate = 0

        # Update GUI gadgets
        self.pres_image.draw() #Plotted image
        self.presLive_label.config(text = "{:.2f} mbar".format(y_pres[-1]))
        self.rateLive_label.config(text = "{:.2f} L/s".format(rate))


    def plotting_PLmic(self,arr): ## Triggered by sensor
        # Setting up looks of graph
        self.ax1.clear()
        self.ax1.set_title ("Color distribution", fontsize=14)
        self.ax1.set_ylabel("Counts", fontsize=12)
        self.ax1.set_xlabel("Color Hue", fontsize=12)
        plt.rcParams['xtick.top'] = True

        # Plot the stuff
        n_bins = 180
        counts,_,_ = self.ax1.hist(arr, n_bins)

        # Update GUI gadgets
        self.ax1.text(0.1, 0.9,'Max at {}'.format(np.argmax(counts)), transform=self.ax1.transAxes)
        self.ax1.set_aspect(1.0/self.ax1.get_data_ratio()*self.plot_ratio)
        self.PLNo_image.draw()

        return counts



    def plotting_PLspectra(self, y_cnt): ## Triggered by loop
        # Setting up looks of graph
        self.ax1.clear()
        self.ax1.set_title ("Wavelength", fontsize=14)
        self.ax1.set_ylabel("Counts", fontsize=12)
        self.ax1.set_xlabel("Wavelength (nm)", fontsize=12)

        x_wav = self.spec_waveL

        self.ax1.plot(x_wav, y_cnt, 'b-')
        self.ax1.text(0.1, 0.9,'Max at {}'.format(round(x_wav[np.argmax(y_cnt)],0)), transform=self.ax1.transAxes)
        # self.ax1.xaxis.set_tick_params(labeltop='on')
        plt.rcParams['xtick.top'] = True
        self.ax1.set_aspect(1.0/self.ax1.get_data_ratio()*self.plot_ratio)
        self.PLNo_image.draw()
        # plt.show()


    def make_heatplot(self, data, fileNameStr, dtype): ## Triggered at the End
        plt.figure(figsize=[4,3])
        if dtype == "gray":
            plt.ylabel("Grayscale percentage")
            plt.yticks(np.linspace(0,255,8),np.around(np.linspace(0,100,8),decimals=0))
            plt.title("Change on Grayscale")
        elif dtype == "hue":
            plt.ylabel("Hue scale")
            plt.yticks(np.linspace(0,180,8),["Orange", "Yellow", "Green", "Turquoise", "Blue", "Purple", "Pink", "Red"])
            plt.title("Change on Hue")
        else:
            plt.ylabel("Wavelength (nm)")
            waveLen = len(self.spec_waveL)
            PLmin = np.min(self.spec_waveL)
            PLmax = np.max(self.spec_waveL)
            plt.yticks(np.linspace(0,waveLen,8),np.around(np.linspace(PLmin,PLmax,8),decimals=0))
            plt.title("PL spectra")

        plt.xlabel("Time(seconds)")
        plt.xticks(np.linspace(0,len(data.columns),8),np.around(np.linspace(0, max(data.columns), 8),decimals=2))
        plt.pcolor(data)

        # ax.pcolor(self.microHue_df)
        plt.savefig(fileNameStr+"_heat_plot.png")#,bbox_inches = "tight")   # save the figure to file
        plt.close()    # close the figure window


    def final_pressure_plot(self): ## Triggered at the End
        time = np.array(self.timeElapArray)
        pres = np.array(self.pressureArray)
        
        fast_i = 0
        long_i = 0
        
        # rvals = []
        # ivals = []
        offset = 2
        
        for i,p in enumerate(pres[offset:]):
            _, _, r_value, _, _ = stats.linregress(time[:i+offset],np.log(pres[:i+offset]))
            if r_value < -0.85:
                fast_i = i

        long_i=np.argmin(pres)

        slope, intercept, r_value, p_value, std_err = stats.linregress(time[:fast_i],np.log(pres[:fast_i]))
        line = np.exp(slope*time+intercept)

        fig = plt.figure(figsize=[4,3])
        ax = fig.add_subplot(1,1,1)
        ax.set_xlabel("Time(sec)")
        ax.set_ylabel("Pressure(mbar)")
        
        ax.semilogy(time,pres,"ro")
        ax.plot(time[:fast_i],line[:fast_i],"-g")
        
        # Preparing data to be saved on metadata file
        ini_pres = pres[0]
        fast_rate = round((ini_pres-pres[fast_i])/time[fast_i],3)
        slow_rate = round((ini_pres-pres[long_i])/time[long_i],3)
        time_vacuum = round(time[long_i],2)
        mini_pres = round(pres[long_i],2)
        time_flux = round(time[-1]-time[long_i+offset],2)
        pres_flux = round(np.mean(pres[long_i+offset:-offset]),2)
        total_time = round(time[-1],2)
        
        ax.text(0.1, 0.7,"{:.2f} mbar/sec".format(fast_rate), transform=ax.transAxes)
        ax.text(0.15, 0.3,"{:.2f} mbar/sec".format(slow_rate), transform=ax.transAxes)
        ax.text(0.3, 0.1,"{:.2f} seconds".format(time_vacuum), transform=ax.transAxes)
        ax.text(0.3, 0.05,"{:.2f} mbar".format(mini_pres), transform=ax.transAxes)
        ax.text(0.6, 0.9,"{:.2f} seconds".format(time_flux), transform=ax.transAxes)
        ax.text(0.6, 0.95,"{:.2f} mbar".format(pres_flux), transform=ax.transAxes)
        # ax.set_aspect(1.0/ax.get_data_ratio()*self.plot_ratio)
    
        fig.savefig(self.full_path+self.sample_name+"_Pressure_plot.png",bbox_inches = "tight")
    
        ## save to dictionary
        dict_names = ["PV_StartingPressure(mbar)","PV_FastVacuumRate(mbar/s)","PV_TotalVacumRate(mbar/s)",
                      "PV_TimeUnderVacuum(s)", "PV_MinimumPressure(mbar)","PV_TimeUnderFlux(s)",
                      "PV_FluxPressure(mbar)","PV_TotalTime(s)","PV_SlopeInterceptRvalue"]#,"PV_abc{a*exp(x*b)+d}"]
        dict_value = [ini_pres,fast_rate,slow_rate,
                      time_vacuum, mini_pres, time_flux,
                      pres_flux, total_time, [round(slope,4),round(intercept,4),round(r_value,4)]]#,*popt]
        for p,dns in enumerate(dict_names):
            self.xml_data[dns] = dict_value[p]




    ## ~o~o~o~o~o~o~o~o Operational functions o~o~o~o~o~o~o~o~
    def solo_mode(self):
        time_step = 0.25
        # delay = self.delay_intVar.get()
        delay = self.intVar_waitT.get()
        for cdwn in np.arange(delay,0,-time_step):
            self.elapsedVar.set("{:.2f} sec".format(cdwn))
            self.master.update_idletasks()
            time.sleep(time_step)


    def startProcess(self):
        #Change button to "stop"
        print("Start: ",end="")
        self.stopButton.grid(row=5,column=0, columnspan=2)
        self.startButton.grid_forget()

        # self.solo_mode()


        # True to start recording processes
        # self.runningProcess = True

        # Starts timer
        self.starTime = time.time()
        self.delay = float(self.intVar_waitT.get())
        self.startP = True
        print("1",end="")

        # Get data from LP50
        # if self.isXML:
        self.xml_data = xr.gather_data()
        print("2",end="")
        # if len(self.xml_data)>2:
        #     self.set_text_metavalues()
        # else:
        #     pass
        #     self.xml_data = {}
        self.get_entry_metavalues()

        # Create Folders
        self.create_date_folder()
        self.create_sample_folder()
        print("3",end="")
        #Refreshes dataframes and arrays
        if self.isMic:
            self.microHue_df = pd.DataFrame()
            self.hueGray_df = pd.DataFrame()
            self.frame_counter = 0
        if self.isSpectro:
            self.PLspec_df = pd.DataFrame()
            # self.PLspec_df["Wavelength(nm)"] = self.spec_waveL
        if self.isPressure:
            self.Pressure_DF = pd.DataFrame()
        else:
            pyautogui.click(35,105)
        print("4",end="")

        self.timeElapArray =[]
        self.pressureArray=[]
        print("5",end="")


    def stopProcess(self):
        #Change button to "start"
        self.stopButton.grid_forget()
        self.startButton.grid(row=5,column=0, columnspan=2)

        # False to stop recording processes
        self.runningProcess = False

        self.list_measured_samples()

        ## Save data
        file_path = self.full_path+self.sample_name
        if self.isMic:
            self.microHue_df = self.microHue_df.astype("int64")
            self.hueGray_df = self.hueGray_df.astype("int64")
            self.microHue_df.to_csv(file_path+"_hue_data.csv",index=False)
            self.hueGray_df.to_csv(file_path+"_hueGrayscale_data.csv",index=False)
            self.fig_pls.savefig(file_path+"_hue_plot.png")
            # print(self.microHue_df)
            self.make_heatplot(self.microHue_df,file_path+"_hue","hue")
            self.make_heatplot(self.hueGray_df,file_path+"_gray","gray")

        if self.isPressure:
            self.Pressure_DF["time"]=self.timeElapArray
            self.Pressure_DF["pressure"]=self.pressureArray
            self.Pressure_DF.to_csv(file_path+"_pressure_data.csv",index=False)
            try:
                self.final_pressure_plot()
            except:
                pass

        if self.isSpectro:
            self.PLspec_df = self.PLspec_df.astype("float64")
            self.make_heatplot(self.PLspec_df,file_path+"_PL","PL")
            self.PLspec_df.insert(loc=0, column="Wavelength(nm)", value=self.spec_waveL)
            self.PLspec_df.to_csv(file_path+"_PL_data.csv",index=False)

        metad = pd.DataFrame.from_dict(self.xml_data, orient='index')
        metad.to_csv(file_path+"_metadata.csv")
        self.elapsedLabel.config(style ="bigST.TLabel")
        # self.xml_data.to_csv(self.folder_path+self.sample_name+"\\"+sample_name+"_metadata_data.csv")

    def processes_loop(self):
        if self.startP:
            time_elapsed = round(time.time()-self.starTime,2)
            time_disp = self.delay-time_elapsed
            if time_disp > 0:
                
                # print(self.delay, round(time.time()-self.starTime,2))
                self.elapsedVar.set("{:.2f} sec".format(time_disp))
                self.master.update_idletasks()
    
            else:
                # print("out "+self.delay, round(time.time()-self.starTime,2))
                self.starTime = time.time()
                self.runningProcess = True
                self.startP = False
        else:
            pass


        if self.runningProcess:
            time_elapsed = round(time.time()-self.starTime,2)
            alt = 3 #Alert time to stop
            cdt = 3 #Cool down time
            total_time = self.intVar_totalT.get() + cdt
            #self.elapsedLabel.set(text=timeEl)
            self.timeElapArray.append(time_elapsed)
            if self.isMic:
                self.readSensor_Microscope(time_elapsed)###
                self.microHue_df[time_elapsed] = self.countsHue #from plotting spectra
                self.hueGray_df[time_elapsed] = self.countsGray
            if self.isPressure:
                self.readSensor_Pressure(time_elapsed)##
            if self.isSpectro:
                spec_counts = self.readSensor_Spectrometer()
                self.PLspec_df[time_elapsed] = spec_counts

            self.elapsedVar.set("{:.2f} sec".format(time_elapsed))

            if total_time-cdt-alt <time_elapsed:
                self.elapsedLabel.config(style ="redST.TLabel")
            if total_time-cdt < time_elapsed:
                self.elapsedLabel.config(style ="blueST.TLabel")
            if total_time < time_elapsed:
                self.stopProcess()

            self.master.update_idletasks()
            
        else:
            if self.isPressure:
                self.readSensor_Pressure(0)
            if self.isMic:
                self.readSensor_Microscope(0)###
            if self.isSpectro:
                self.readSensor_Spectrometer()

        if self.isCam:
            self.readSensor_Camera()###


        if self.fps_entry.get() == "":
            fps_get = 30
            self.fps_entry.set("30")

        else:
            fps_get = int(self.fps_entry.get())


        dur = int(1000/fps_get)
        self.master.after(dur, self.processes_loop)

    def close_window(self):
        if self.isMic:
            self.cap_MIC.release()
            cv2.destroyAllWindows()
        # if self.isCam:
        #     self.cap_CAM.release()
        #     cv2.destroyAllWindows()
        if self.isPressure:
            self.pressureSensor.close()
        if self.isSpectro:
            self.spec.close()
        # self.stopEvent.set()
        # self.master.destroy()
        self.root.destroy()

        Tk().destroy()
        sys.exit()
        

VacGUI = Vacuum_GUI()
VacGUI.root.mainloop()






