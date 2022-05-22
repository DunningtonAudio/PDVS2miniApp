#!/usr/bin/env python

from serial import *
from serial.tools import list_ports
from decimal import *
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from time import sleep
from os.path import exists

mini =  Serial() #create serial instance for use later
setvoltage = '**.*****' #string to represent the voltage we want to set
outvoltage = '*.**' #string representing the measured output voltage read from the PDVS2mini
battcurrent = '*.**' #string representing the measured battery current read from the PDVS2mini
battvoltage = '*.**' #string representing the measured battery voltage read from the PDVS2mini
preState = 'Lock'
defaults = [] #list of preset values
menulist = [] #list of serial ports

if exists('PDVS2mini.conf'): #import user defined defaults if available
    try:
        f = open('PDVS2mini.conf','r')
        lines = f.readlines()
        firstLine = lines[0].strip()
        if (firstLine == 'Edit' or firstLine == 'Lock'):
            preState = firstLine
            lines.pop(0)
        for line in lines:
            defaults.append(line.strip())
        if len(defaults) < 10:
                defaults += [''] * (10 - len(defaults))
    except:
        print('Error reading defaults')
else:
    defaults = ['1.00000','2.00000','3.00000','4.00000','5.00000','6.00000','7.00000','8.00000','9.00000','10.00000'] #built in preset defaults

def validate(value):
    global setvoltage
    try:
        if '.' in value: #check if we have a decimal place
            pointpos = value.index('.')
            setvoltage = value[:(pointpos + 6)] #get rid of any precision beyond 5dp
        else:
            setvoltage = value
        validSet = Decimal(setvoltage) #try to convert to a Decimal
        if(validSet >= 0 and validSet <= 10):#check that it's in range
            print("Input value ok")
            return True
        else:
            print("Input value out of range")
            return False
    except:
        print("Value entered is not a number between 0.00000 and 10.00000")
        return False

window = Tk()
window.title("PDVS2mini")
window.geometry('530x450')
window.resizable(width=False, height=False)

tab_control = ttk.Notebook(window)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab_control.add(tab1, text = "Operate")
#tab_control.add(tab2, text = "Cal/Settings") < FOR FUTURE DEVELOPMENT
tab_control.pack(expand=1, fill=X, anchor=N)

#frame for dealing with serial connection:

comFrame = Frame(tab1)
comFrame.pack(expand=1, fill=BOTH)

comLabel = Label(comFrame, text="Serial Port:")
comLabel.pack(side=LEFT, padx=10)

portlist = Combobox(comFrame, width=16, values=menulist)
portlist.pack(side=LEFT)

def refreshPorts():
    global menulist
    try:
        ports = list_ports.comports() #get a list of serial port objects
        menulist = [] #list object for dropdown
        for port in ports: #populate dropdown list with human readable device names
            menulist.append(port.device)
        portlist.configure(values = menulist)
        return True
    except:
        print("Error building port list")
        return False

def connect():
    portlist.configure(state='disable')
    port = portlist.get()
    if port == '':                                                                                  #check if there is a com port selected
        messagebox.showwarning('Connection error', 'Please select a serial port to connect to')     #if not pop up a thing saying select a com port
        portlist.configure(state='normal')
        return
    if btnConnect["text"] == "Disconnect":                                                          #if we are currently connected...
        print("Closing connection to serial port " + port + " ...")
        mini.close()                                                                                #disconnect
        btnConnect["text"] = "Connect"
        setLabel['text'] = "**.*****"
        outLabel['text'] = "**.**"
        battFB['text'] = "**.*"
        portlist.configure(state='normal')
        return
    else:
        try:
            mini.port = port                                                                        #set up serial port using selected interface
            mini.baudrate = 250000
            mini.bytesize = 8
            mini.parity = "N"
            mini.stopbits = 1
            mini.timeout = None
            mini.xonxoff = 0
            mini.rtscts = 0
            mini.dsrdtr = 0
            print("Connecting to serial port " + port + "...")
            mini.open()                                                                             #open the port
            btnConnect["text"] = "Disconnect"
        except:
            if 'mini' in globals():
                messagebox.showerror('Connection error', 'The selected port is not available.\n\nIt could have been disconnected or be in use by another application.')
                print('Exception encountered during connection')
                mini.close()
                portlist.configure(state='normal')

btnConnect = Button(comFrame, text="Connect", command=connect)
btnConnect.pack(side=LEFT, padx=10, pady=10)

s1Frame = Frame(tab1)
s1Frame.pack(expand=1, fill=BOTH)

s1 = ttk.Separator(s1Frame, orient='horizontal')
s1.pack(expand=1, fill=X, padx=5)

#frame for displaying and setting output:

outFrame = Frame(tab1)
outFrame.pack(expand=1, fill=BOTH)

vLabel = Label(outFrame, text="Set Voltage:").pack(side=LEFT, padx=10)

setEnt = Entry(outFrame, state='normal', width=16)
setEnt.insert(0, '0.00000')
setEnt.pack(side=LEFT)

def setOutput(value):
    global setvoltage
    if ('mini' in globals() and mini.is_open):
        if validate(value):
            outstring = '<KeyVoltage,0,' + setvoltage + '>\n'
            mini.write(outstring.encode('ascii'))
            print("Setting output to " + setvoltage + "V.")
        else:
            messagebox.showwarning('Input error', 'Set voltage is not a decimal value between 0.00000 and 10.00000\nPlease enter a valid set voltage')
    else:
        messagebox.showwarning('Connection error', 'No connection to PDVS2mini, cannot set output')
        print("No connection to PDVS2mini, cannot set output")

setBut = Button(outFrame, text="Apply", command=lambda: setOutput(setEnt.get())).pack(side=LEFT, padx=10)

setLabel = Label(outFrame, text=setvoltage, background="black", foreground="white", font=('TkDefaultFont',24), relief=SUNKEN, anchor=E, width=8)
setLabel.pack(expand=0, fill=NONE, side=RIGHT, padx=10, pady=5)

fbFrame = Frame(tab1)
fbFrame.pack(expand=1, fill=BOTH)

outLabel = Label(fbFrame, text=outvoltage, background="black", foreground="white", font=('TkDefaultFont',16), relief=SUNKEN, anchor=E, width=5)
outLabel.pack(side=RIGHT, padx=10, pady=5)

fbLabel = Label(fbFrame, text='Readback:').pack(side=RIGHT, padx=10)

s2Frame = Frame(tab1)
s2Frame.pack(expand=1, fill=BOTH)

s2 = ttk.Separator(s2Frame, orient='horizontal')
s2.pack(expand=1, fill=X, padx=5)

#frame for preset buttons

preFrame = Frame(tab1)
preFrame.pack(expand=1, fill=BOTH)

preHeader = Label(preFrame, text="Presets:").pack(side=LEFT, padx=10)

def toggle():
    if preToggle["text"] == 'Lock':
        btn0Ent.configure(state='readonly')
        btn1Ent.configure(state='readonly')
        btn2Ent.configure(state='readonly')
        btn3Ent.configure(state='readonly')
        btn4Ent.configure(state='readonly')
        btn5Ent.configure(state='readonly')
        btn6Ent.configure(state='readonly')
        btn7Ent.configure(state='readonly')
        btn8Ent.configure(state='readonly')
        btn9Ent.configure(state='readonly')
        preToggle["text"] = 'Edit'
        return
    else:
        btn0Ent.configure(state='normal')
        btn1Ent.configure(state='normal')
        btn2Ent.configure(state='normal')
        btn3Ent.configure(state='normal')
        btn4Ent.configure(state='normal')
        btn5Ent.configure(state='normal')
        btn6Ent.configure(state='normal')
        btn7Ent.configure(state='normal')
        btn8Ent.configure(state='normal')
        btn9Ent.configure(state='normal')
        preToggle["text"] = 'Lock'
        return

preToggle = Button(preFrame, text=preState, command=toggle)
preToggle.pack(side=LEFT, padx=10, pady=10)

preSpace01 = Frame(tab1)
preSpace01.pack(expand=1, fill=BOTH)

preF0 = Frame(preSpace01)
preF0.pack(side=LEFT, expand=1, fill=BOTH)

btn0Ent = Entry(preF0, state='normal', width=16)
btn0Ent.insert(0, defaults[0])
btn0Ent.pack(side=LEFT, padx=10)

btn0 = Button(preF0, text="Apply", command=lambda: setOutput(btn0Ent.get())).pack(side=LEFT, padx=5, pady=5)

preF1 = Frame(preSpace01)
preF1.pack(side=LEFT, expand=1, fill=BOTH)

btn1Ent = Entry(preF1, state='normal', width=16)
btn1Ent.insert(0, defaults[1])
btn1Ent.pack(side=LEFT, padx=10)

btn1 = Button(preF1, text="Apply", command=lambda: setOutput(btn1Ent.get())).pack(side=LEFT, padx=5, pady=5)

preSpace23 = Frame(tab1)
preSpace23.pack(expand=1, fill=BOTH)

preF2 = Frame(preSpace23)
preF2.pack(side=LEFT, expand=1, fill=BOTH)

btn2Ent = Entry(preF2, state='normal', width=16)
btn2Ent.insert(0, defaults[2])
btn2Ent.pack(side=LEFT, padx=10)

btn2 = Button(preF2, text="Apply", command=lambda: setOutput(btn2Ent.get())).pack(side=LEFT, padx=5, pady=5)

preF3 = Frame(preSpace23)
preF3.pack(side=LEFT, expand=1, fill=BOTH)

btn3Ent = Entry(preF3, state='normal', width=16)
btn3Ent.insert(0, defaults[3])
btn3Ent.pack(side=LEFT, padx=10)

btn3 = Button(preF3, text="Apply", command=lambda: setOutput(btn3Ent.get())).pack(side=LEFT, padx=5, pady=5)

preSpace45 = Frame(tab1)
preSpace45.pack(expand=1, fill=BOTH)

preF4 = Frame(preSpace45)
preF4.pack(side=LEFT, expand=1, fill=BOTH)

btn4Ent = Entry(preF4, state='normal', width=16)
btn4Ent.insert(0, defaults[4])
btn4Ent.pack(side=LEFT, padx=10)

btn4 = Button(preF4, text="Apply", command=lambda: setOutput(btn4Ent.get())).pack(side=LEFT, padx=5, pady=5)

preF5 = Frame(preSpace45)
preF5.pack(side=LEFT, expand=1, fill=BOTH)

btn5Ent = Entry(preF5, state='normal', width=16)
btn5Ent.insert(0, defaults[5])
btn5Ent.pack(side=LEFT, padx=10)

btn5 = Button(preF5, text="Apply", command=lambda: setOutput(btn5Ent.get())).pack(side=LEFT, padx=5, pady=5)

preSpace67 = Frame(tab1)
preSpace67.pack(expand=1, fill=BOTH)

preF6 = Frame(preSpace67)
preF6.pack(side=LEFT, expand=1, fill=BOTH)

btn6Ent = Entry(preF6, state='normal', width=16)
btn6Ent.insert(0, defaults[6])
btn6Ent.pack(side=LEFT, padx=10)

btn6 = Button(preF6, text="Apply", command=lambda: setOutput(btn6Ent.get())).pack(side=LEFT, padx=5, pady=5)

preF7 = Frame(preSpace67)
preF7.pack(side=LEFT, expand=1, fill=BOTH)

btn7Ent = Entry(preF7, state='normal', width=16)
btn7Ent.insert(0, defaults[7])
btn7Ent.pack(side=LEFT, padx=10)

btn7 = Button(preF7, text="Apply", command=lambda: setOutput(btn7Ent.get())).pack(side=LEFT, padx=5, pady=5)

preSpace89 = Frame(tab1)
preSpace89.pack(expand=1, fill=BOTH)

preF8 = Frame(preSpace89)
preF8.pack(side=LEFT, expand=1, fill=BOTH)

btn8Ent = Entry(preF8, state='normal', width=16)
btn8Ent.insert(0, defaults[8])
btn8Ent.pack(side=LEFT, padx=10)

btn8 = Button(preF8, text="Apply", command=lambda: setOutput(btn8Ent.get())).pack(side=LEFT, padx=5, pady=5)

preF9 = Frame(preSpace89)
preF9.pack(side=LEFT, expand=1, fill=BOTH)

btn9Ent = Entry(preF9, state='normal', width=16)
btn9Ent.insert(0, defaults[9])
btn9Ent.pack(side=LEFT, padx=10)

btn9 = Button(preF9, text="Apply", command=lambda: setOutput(btn9Ent.get())).pack(side=LEFT, padx=5, pady=5)

#s3Frame = Frame(tab1)
#s3Frame.pack(expand=1, fill=BOTH)

#s3 = ttk.Separator(s3Frame, orient='horizontal')
#s3.pack(expand=1, fill=X, padx=5)

#frame for battery info

battFrame = Frame(window)
battFrame.pack(side=BOTTOM, expand=1, fill=BOTH)

battLabel = Label(battFrame, text="Battery Voltage:")
battLabel.pack(side=LEFT, padx=10)

battFB = Label(battFrame, text=battvoltage, background="black", foreground="white", relief=SUNKEN, anchor=E, width=5)
battFB.pack(side=LEFT, pady=5)

calFrame = Frame(tab2)
calFrame.pack()

toggle() #initialise lock state

def refresh():
    #print("Refresh called")
    if mini.is_open:
        glomp = []
        mini.flushInput()
        while len(glomp) < 23:
            glomp.append(mini.readline())   #read 23 lines to ensure we have all data
        del glomp[0]                    #discard the first line which might be incomplete
        for x in glomp:                 #loop through lines and update each variable/display label
            temp = x.decode('ascii').strip("\r\n")
            if temp[0:3] == "KV,":
                setLabel['text'] = temp[5:] #update the set voltage value
            elif temp[0:4] == "OVF,":
                outLabel['text'] = temp[6:] #update the measured voltage value
            elif temp[0:3] == "BV,":
                battFB['text'] = temp[5:]   #update the measured battery voltage
            elif temp[0:4] == "BLI,":
                battStatus = temp[6:]
                if battStatus == "Status - Ok": #set the colour of the battery voltage display
                    battFB['foreground'] = "green2"
                else:
                    battFB['foreground'] = "red"
        if abs(float(outLabel['text']) - float(setLabel['text'])) < 0.045: #set the colour of the measured voltage display
            outLabel['foreground'] = "green2"
        else:
            outLabel['foreground'] = "red"
        del glomp
    else:
        refreshPorts()
        battFB['foreground'] = "white"
        outLabel['foreground'] = "white"
    window.after(200, refresh)
            #return#call after again - every 200ms?

window.after(0, refresh)
window.mainloop()
