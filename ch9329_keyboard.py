#!/usr/bin/env python3
import tkinter
import ctypes
from tkinter import ttk
from tkinter import IntVar
from tkinter import StringVar
from tkinter import BooleanVar
import serial
import serial.tools
import serial.tools.list_ports
import serial.tools.hexlify_codec
import math
import binascii

try:#windows
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
except:
    ScaleFactor=75

root=tkinter.Tk()
root.tk.call('tk', 'scaling', ScaleFactor/75)
root.title("CH9329 Serial HID Control")
root.geometry("1600x400+300+300")

style=ttk.Style()
try:
    style.theme_use("vista")
except:
    style.theme_use("default")
style.configure('Horizontal.TScrollbar',arrowsize=20)
style.configure('Vertical.TScrollbar',arrowsize=20)
style.map('active.TButton',background=[("active","LightBlue1"),("!disabled","LightBlue2")])

def bitArrayToInt(array):
    num=int()
    length=len(array)
    for i in range(0,length):
        if array[i]:
            num=num+2**(length-i-1)
    return num

#var
portVar=StringVar()
portVar.set("None")
baudVar=IntVar()
baudVar.set(115200)
captureCheckVar=BooleanVar()
captureCheckVar.set(True)
stickyCheckVar=BooleanVar()
stickyCheckVar.set(True)
debugCheckVar=BooleanVar()
debugCheckVar.set(False)
address=0x00
serialPort=None
#port
def hexWrite(port,hexdata):
    packet=bytearray()
    for byte in hexdata:
        packet.append(byte)
    port.write(packet)
def hexRead(port,size):
    output=bytearray()
    packet=port.read(size)
    for byte in packet:
        output.append(byte)
    return output
def read9329(port):
    packet=bytearray()
    head=hexRead(port,size=5)
    size=head[4]
    data=hexRead(port,size)
    sumx=hexRead(port,1)[0]
    for byte in head:
        packet.append(byte)
    for byte in data:
        packet.append(byte)
    cmd=packet[3]
    sumy=int()
    for byte in packet:
        sumy+=byte
    sumy=sumy%256
    if sumx==sumy:
        sumpass=True
    else:
        sumpass=False
    packet.append(sumx)
    if debugCheckVar.get():
        outlist=[]
        for byte in packet:
            outlist.append(format(byte, '02x'))
        serialOutput.insert("end",f"->{outlist},pass:{sumpass}")
        serialOutput.see(serialOutput.size())
    if sumpass:
        if cmd==0x81:
            ver=data[0]
            usb=data[1]
            infolabel.config(text=f"Ver:{hex(ver)},USB:{usb}")
            lock="{:0>8b}".format(data[2])
            locklabel.config(text=f"Num{lock[-1]} Caps{lock[-2]} Scroll{lock[-3]}")
def write9329(port,addr,cmd,data):
    try:
        packet=bytearray()
        packet.append(0x57)
        packet.append(0xab)
        packet.append(addr)
        packet.append(cmd)
        packet.append(len(data))
        for byte in data:
            packet.append(byte)
        sumy=int()
        for byte in packet:
            sumy+=byte
        sumy=sumy%256
        packet.append(sumy)
        hexWrite(port,packet)
        if debugCheckVar.get():
            showlist=[]
            for byte in packet:
                showlist.append(format(byte, '02x'))
            serialOutput.insert("end",f"<-{showlist}")
            serialOutput.see(serialOutput.size())
        read9329(port)
    except Exception as exc:
        serialOutput.insert("end",f"{exc}\n")
        serialOutput.see(serialOutput.size())
#SerialSel
def openSerial():
    global pressedKeysCont,pressedKeysNormal
    pressedKeysCont=[0,0,0,0,0,0,0,0]
    for i in [0,1,2,3,4,5,6,7]:
        listButtonCtrl[i].config(style="TButton")
    pressedKeysNormal=bytearray()
    keyFrame.focus_set()
    try:
        global serialPort
        serialPort=serial.Serial(port=portVar.get(),baudrate=baudVar.get())
        serialPort.timeout=2
        linkButton.configure(text="Close Port",command=closeSerial)
        portBox.configure(state="disabled")
        baudBox.configure(state="disabled")
        write9329(serialPort,address,0x01,bytearray())
    except Exception as exc:
        linkButton.configure(text="Open Error")
        serialOutput.insert("end",f"{exc}\n")
        serialOutput.see(serialOutput.size())
def closeSerial():
    global serialPort
    serialPort.close()
    linkButton.configure(text="Open Port",command=openSerial)
    portBox.configure(state="normal")
    baudBox.configure(state="normal")
def refreshPorts():
    portlist=serial.tools.list_ports.comports()
    portMenu.delete(0, "end")
    portMenu.add_command(label="Refresh",command=refreshPorts)
    portNameList=[]
    for port in portlist:
        portMenu.add_radiobutton(label=str(port),variable=portVar,value=port.device)
        portNameList.append(port.device)
#Keyboard
dictKeyCont=dict({
    65507:7,#LCTRL
    65505:6,#LSHIFT
    65513:5,#LALT
    65511:5,#LMETA
    65515:4,#LSUPER
    65371:4,#LWIN
    65508:3,#RCTRL
    65506:2,#RSHIFT
    65514:1,#RALT
    65512:1,#RMETA
    65516:0,#RSUPER
    65372:0,#RWIN
    })
dictKeyNormal=dict({
    65307:0x29,#Esc
    65470:0x3a,#F1
    65471:0x3b,#F2
    65472:0x3c,#F3
    65473:0x3d,#F4
    65474:0x3e,#F5
    65475:0x3f,#F6
    65476:0x40,#F7
    65477:0x41,#F8
    65478:0x42,#F9
    65479:0x43,#F10
    65480:0x44,#F11
    65481:0x45,#F12
    65377:0x46,#Print
    65301:0x46,#Print
    65300:0x47,#ScrollLock
    65299:0x48,#PauseBreak
    96:0x35,#`
    49:0x1e,#1
    50:0x1f,#2
    51:0x20,#3
    52:0x21,#4
    53:0x22,#5
    54:0x23,#6
    55:0x24,#7
    56:0x25,#8
    57:0x26,#9
    48:0x27,#0
    45:0x2d,#-
    61:0x2e,#=
    126:0x35,#~
    33:0x1e,#!
    64:0x1f,#@
    35:0x20,##
    36:0x21,#$
    37:0x22,#%
    94:0x23,#^
    38:0x24,#&
    42:0x25,#*
    40:0x26,#(
    41:0x27,#)
    95:0x2d,#_
    43:0x2e,#+
    65288:0x2a,#Backspace
    65289:0x2b,#Tab
    65056:0x2b,#BackTab
    113:0x14,#q
    119:0x1a,#w
    101:0x08,#e
    114:0x15,#r
    116:0x17,#t
    121:0x1c,#y
    117:0x18,#u
    105:0x0c,#i
    111:0x12,#o
    112:0x13,#p
    91:0x2f,#[
    93:0x30,#]
    92:0x31,#\
    81:0x14,#Q
    87:0x1a,#W
    69:0x08,#E
    82:0x15,#R
    84:0x17,#T
    89:0x1c,#Y
    85:0x18,#U
    73:0x0c,#I
    79:0x12,#O
    80:0x13,#P
    123:0x2f,#{
    125:0x30,#}
    124:0x31,#|
    65509:0x39,#Caps
    97:0x04,#a
    115:0x16,#s
    100:0x07,#d
    102:0x09,#f
    103:0x0a,#g
    104:0x0b,#h
    106:0x0d,#j
    107:0x0e,#k
    108:0x0f,#l
    59:0x33,#;
    39:0x34,#'
    65:0x04,#A
    83:0x16,#S
    68:0x07,#D
    70:0x09,#F
    71:0x0a,#G
    72:0x0b,#H
    74:0x0d,#J
    75:0x0e,#K
    76:0x0f,#L
    58:0x33,#:
    34:0x34,#"
    65293:0x28,#Enter
    122:0x1d,#z
    120:0x1b,#x
    99:0x06,#c
    118:0x19,#v
    98:0x05,#b
    110:0x11,#n
    109:0x10,#m
    44:0x36,#,
    46:0x37,#.
    47:0x38,#/
    90:0x1d,#Z
    88:0x1b,#X
    67:0x06,#C
    86:0x19,#V
    66:0x05,#B
    78:0x11,#N
    77:0x10,#M
    60:0x36,#<
    62:0x37,#>
    63:0x38,#?
    32:0x2c,#Space
    65373:0x65,#App
    65383:0x65,#Menu
    65379:0x49,#Insert
    65535:0x4c,#Delete
    65360:0x4a,#Home
    65367:0x4d,#End
    65365:0x4b,#PageUp
    65366:0x4e,#PageDown
    65361:0x50,#Left
    65362:0x52,#Up
    65363:0x4f,#Right
    65364:0x51,#Down
    })
dictKeyMedia=dict({})
pressedKeysCont=[0,0,0,0,0,0,0,0]
pressedKeysNormal=bytearray()
pressedKeysMedia=[]
def sendKeys():
    global serialPort,address,pressedKeysNormal,pressedKeysCont,pressedKeysMedia,listButtonCtrl,pressedKeysCont
    packet=bytearray()
    packet.append(bitArrayToInt(pressedKeysCont))
    packet.append(0x00)
    data2=bytearray(pressedKeysNormal)
    while len(data2)<6:
        data2.append(0x00)
    for byte in data2:
        packet.append(byte)
    write9329(port=serialPort,addr=address,cmd=0x02,data=packet)
    write9329(serialPort,address,0x01,bytearray())
def pressNormal(hidcode):
    global pressedKeysNormal,dictButtonsNormal
    if pressedKeysNormal.find(hidcode)!=-1:
        pass
    else:
        if len(pressedKeysNormal)<=6:
            pressedKeysNormal.append(hidcode)
            if dictButtonsNormal.get(hidcode,None):
                dictButtonsNormal.get(hidcode).config(style="active.TButton")
            sendKeys()
def releaseNormal(hidcode):
    global pressedKeysNormal,dictButtonsNormal
    try:
        pressedKeysNormal.remove(hidcode)
        if dictButtonsNormal.get(hidcode,None):
            dictButtonsNormal.get(hidcode).config(style="TButton")
        sendKeys()
    except:
        pass
def pressCont(index,press):
    global pressedKeysCont
    if press==-1:
        press=1-pressedKeysCont[index]
    else:
        press=bool(press)
    pressedKeysCont[index]=press
    sendKeys()
    if press:
        listButtonCtrl[index].config(style="active.TButton")
    else:
        listButtonCtrl[index].config(style="TButton")
def pressCapture(event):
    global dictKeyNormal,dictKeyCont,pressedKeysNormal,pressedKeysCont,dictKeyMedia
    keylabel.configure(text=f"Pressed:{event.keysym},{event.keysym_num}")
    keySpace.focus_set()
    if captureCheckVar.get():
        key=event.keysym_num
        if stickyCheckVar.get():
            if dictKeyCont.get(key,None):
                index=dictKeyCont[key]
                pressCont(index,-1)
        else:
            if dictKeyCont.get(key,None):
                index=dictKeyCont[key]
                pressCont(index,1)
        if dictKeyNormal.get(key,None):
            hidcode=dictKeyNormal[key]
            try:
                pressedKeysNormal.index(hidcode)
            except:
                pressNormal(hidcode)
def releaseCapture(event):
    global dictKeyNormal,dictKeyCont,pressedKeysNormal,pressedKeysCont,dictKeyMedia
    keylabel.configure(text=f"Released:{event.keysym},{event.keysym_num}")
    if captureCheckVar.get():
        try:
            key=event.keysym_num
            if stickyCheckVar.get()==False:
                if dictKeyCont.get(key,None):
                    index=dictKeyCont[key]
                    pressCont(index,0)
            if dictKeyNormal.get(key,None):
                releaseNormal(dictKeyNormal[key])
        except Exception as exc:
            print(exc)
            print(pressedKeysNormal)

#Menubar
menubar = tkinter.Menu(root)
portMenu=tkinter.Menu(menubar,tearoff=0,selectcolor="lime")
baudMenu=tkinter.Menu(menubar,tearoff=0,selectcolor="lime")
for baud in [1200,2400,4800,9600,19200,38400,57600,115200]:
     baudMenu.add_radiobutton(label=str(baud),variable=baudVar)
menubar.add_cascade(label="Port", menu=portMenu)
menubar.add_cascade(label="Baud", menu=baudMenu)
#root.config(menu=menubar)


#Info
infoFrame=ttk.Frame(root,width=100)
linkButton=ttk.Button(infoFrame,text="Open Port",command=openSerial)
keylabel=ttk.Label(infoFrame,text="Key=",width=20)
infolabel=ttk.Label(infoFrame,text="Ver:,USB:",width=20)
locklabel=ttk.Label(infoFrame,text="Num0 Caps0 Scroll0")
infoFrame.place(relx=0,rely=0,relwidth=0.2,relheight=1)
linkButton.place(relx=0,rely=0,relwidth=1,relheight=0.1)
keylabel.place(relx=0,rely=0.1,relwidth=1,relheight=0.1)
infolabel.place(relx=0,rely=0.2,relwidth=1,relheight=0.1)
locklabel.place(relx=0,rely=0.3,relwidth=1,relheight=0.1)

portBox=ttk.Menubutton(infoFrame,textvariable=portVar,menu=portMenu)
baudBox=ttk.Menubutton(infoFrame,textvariable=baudVar,menu=baudMenu)
captureCheck=ttk.Checkbutton(infoFrame,text="Capture",variable=captureCheckVar)
captureCheck.place(relx=0,rely=0.5,relwidth=0.3,relheight=0.1)
stickyCheck=ttk.Checkbutton(infoFrame,text="Sticky",variable=stickyCheckVar)
stickyCheck.place(relx=0.3,rely=0.5,relwidth=0.3,relheight=0.1)
debugCheck=ttk.Checkbutton(infoFrame,text="Debug",variable=debugCheckVar)
debugCheck.place(relx=0.6,rely=0.5,relwidth=0.3,relheight=0.1)

portBox.place(relx=0,rely=0.4,relwidth=0.5,relheight=0.1)
baudBox.place(relx=0.5,rely=0.4,relwidth=0.5,relheight=0.1)
serialOutputPanel=ttk.Frame(infoFrame)
serialOutput=tkinter.Listbox(serialOutputPanel)
serialXScroll=ttk.Scrollbar(serialOutputPanel,orient="horizontal",command=serialOutput.xview)
serialYScroll=ttk.Scrollbar(serialOutputPanel,orient="vertical",command=serialOutput.yview)
serialOutput.config(xscrollcommand=serialXScroll.set,yscrollcommand=serialYScroll.set)
serialOutputPanel.place(relx=0,rely=0.6,relwidth=1,relheight=0.4)
serialYScroll.place(relx=1,rely=0,relheight=1,anchor="ne")
serialXScroll.place(relx=0,rely=1,relwidth=1,width=-20,anchor="sw")
serialOutput.place(relx=0,rely=0,relwidth=1,relheight=1,width=-20,height=-20)
#Tabs
tabs=ttk.Notebook(root)
tabs.place(relx=0.2,rely=0,relwidth=0.8,relheight=1)
standardTab=ttk.Frame()
customTab=ttk.Frame()
tabs.add(standardTab,text="Standard")
tabs.add(customTab,text="Custom")
#custom
cmdVar=StringVar()
dataVar=StringVar()
cmdVar.set(0x01)
def customWrite():
    global serialPort,address,cmdVar,dataVar
    write9329(port=serialPort,addr=address,cmd=int(cmdVar.get(),16),data=binascii.a2b_hex(dataVar.get()))
def releaseAll():
    global serialPort,address
    write9329(port=serialPort,addr=address,cmd=0x02,data=bytearray([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]))
    write9329(port=serialPort,addr=address,cmd=0x03,data=bytearray([0x00,0x00]))
customCommandLabel=ttk.Label(customTab,text="Command")
customCommandLabel.place(relx=0,rely=0,relwidth=0.2,relheight=0.1)
customDataLabel=ttk.Label(customTab,text="Data")
customDataLabel.place(relx=0.2,rely=0,relwidth=0.2,relheight=0.1)
customCommand=ttk.Combobox(customTab,textvariable=cmdVar)
customCommand["values"]=["0x01","0x02","0x03","0x04","0x05","0x06","0x87","0x0f"]
customCommand.place(relx=0,rely=0.1,relwidth=0.2,relheight=0.1)
customData=ttk.Entry(customTab,textvariable=dataVar)
customData.place(relx=0.2,rely=0.1,relwidth=0.2,relheight=0.1)
customSend=ttk.Button(customTab,text="Send",command=customWrite)
customSend.place(relx=0.4,rely=0.1,relwidth=0.2,relheight=0.1)
releaseAllButton=ttk.Button(customTab,text="Release All keys",command=releaseAll)
releaseAllButton.place(relx=0.6,rely=0.1,relwidth=0.2,relheight=0.1)


#Keys
def bindButton(button,keycode):
    button.bind("<ButtonPress>",lambda event:pressNormal(keycode))
    button.bind("<ButtonRelease>",lambda event:releaseNormal(keycode))
keyFrame=ttk.Frame(standardTab)
keyFrame.place(relx=0,rely=0,relwidth=0.8,relheight=1)
#Line1
keyEsc=ttk.Button(keyFrame,text="Esc")
keyEsc.place(relx=0,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyEsc,0x29)
keyF1=ttk.Button(keyFrame,text="F1")
keyF1.place(relx=0.05,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF1,0x3a)
keyF2=ttk.Button(keyFrame,text="F2")
keyF2.place(relx=0.1,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF2,0x3b)
keyF3=ttk.Button(keyFrame,text="F3")
keyF3.place(relx=0.15,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF3,0x3c)
keyF4=ttk.Button(keyFrame,text="F4")
keyF4.place(relx=0.2,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF4,0x3d)
keyF5=ttk.Button(keyFrame,text="F5")
keyF5.place(relx=0.3,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF5,0x3e)
keyF6=ttk.Button(keyFrame,text="F6")
keyF6.place(relx=0.35,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF6,0x3f)
keyF7=ttk.Button(keyFrame,text="F7")
keyF7.place(relx=0.4,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF7,0x40)
keyF8=ttk.Button(keyFrame,text="F8")
keyF8.place(relx=0.45,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF8,0x41)
keyF9=ttk.Button(keyFrame,text="F9")
keyF9.place(relx=0.55,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF9,0x42)
keyF10=ttk.Button(keyFrame,text="F10")
keyF10.place(relx=0.6,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF10,0x43)
keyF11=ttk.Button(keyFrame,text="F11")
keyF11.place(relx=0.65,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF11,0x44)
keyF12=ttk.Button(keyFrame,text="F12")
keyF12.place(relx=0.7,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyF12,0x45)
#Line2
keyGrave=ttk.Button(keyFrame,text="~\n`")
keyGrave.place(relx=0,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(keyGrave,0x35)
key1=ttk.Button(keyFrame,text="!\n1")
key1.place(relx=0.05,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key1,0x1e)
key2=ttk.Button(keyFrame,text="@\n2")
key2.place(relx=0.1,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key2,0x1f)
key3=ttk.Button(keyFrame,text="#\n3")
key3.place(relx=0.15,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key3,0x20)
key4=ttk.Button(keyFrame,text="$\n4")
key4.place(relx=0.2,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key4,0x21)
key5=ttk.Button(keyFrame,text="%\n5")
key5.place(relx=0.25,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key5,0x22)
key6=ttk.Button(keyFrame,text="^\n6")
key6.place(relx=0.3,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key6,0x23)
key7=ttk.Button(keyFrame,text="&\n7")
key7.place(relx=0.35,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key7,0x24)
key8=ttk.Button(keyFrame,text="*\n8")
key8.place(relx=0.4,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key8,0x25)
key9=ttk.Button(keyFrame,text="(\n9")
key9.place(relx=0.45,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key9,0x26)
key0=ttk.Button(keyFrame,text=")\n0")
key0.place(relx=0.5,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(key0,0x27)
keyMinus=ttk.Button(keyFrame,text="_\n-")
keyMinus.place(relx=0.55,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(keyMinus,0x2d)
keyEquals=ttk.Button(keyFrame,text="+\n=")
keyEquals.place(relx=0.6,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(keyEquals,0x2e)
keyBackspace=ttk.Button(keyFrame,text="Backspace")
keyBackspace.place(relx=0.65,rely=0.25,relwidth=0.1,relheight=0.15)
bindButton(keyBackspace,0x2a)
#Line3
keyTab=ttk.Button(keyFrame,text="Tab")
keyTab.place(relx=0,rely=0.4,relwidth=0.075,relheight=0.15)
bindButton(keyTab,0x2b)
keyQ=ttk.Button(keyFrame,text="Q")
keyQ.place(relx=0.075,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyQ,0x14)
keyW=ttk.Button(keyFrame,text="W")
keyW.place(relx=0.125,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyW,0x1a)
keyE=ttk.Button(keyFrame,text="E")
keyE.place(relx=0.175,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyE,0x08)
keyR=ttk.Button(keyFrame,text="R")
keyR.place(relx=0.225,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyR,0x15)
keyT=ttk.Button(keyFrame,text="T")
keyT.place(relx=0.275,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyT,0x17)
keyY=ttk.Button(keyFrame,text="Y")
keyY.place(relx=0.325,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyY,0x1c)
keyU=ttk.Button(keyFrame,text="U")
keyU.place(relx=0.375,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyU,0x18)
keyI=ttk.Button(keyFrame,text="I")
keyI.place(relx=0.425,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyI,0x0c)
keyO=ttk.Button(keyFrame,text="O")
keyO.place(relx=0.475,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyO,0x12)
keyP=ttk.Button(keyFrame,text="P")
keyP.place(relx=0.525,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyP,0x13)
keyLBracket=ttk.Button(keyFrame,text="{\n[")
keyLBracket.place(relx=0.575,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyLBracket,0x2f)
keyRBracket=ttk.Button(keyFrame,text="}\n]")
keyRBracket.place(relx=0.625,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyRBracket,0x30)
keyBackslash=ttk.Button(keyFrame,text="|\n\\")
keyBackslash.place(relx=0.675,rely=0.4,relwidth=0.075,relheight=0.15)
bindButton(keyBackslash,0x31)
#Line4
keyCaps=ttk.Button(keyFrame,text="Caps")
keyCaps.place(relx=0,rely=0.55,relwidth=0.1,relheight=0.15)
bindButton(keyCaps,0x39)
keyA=ttk.Button(keyFrame,text="A")
keyA.place(relx=0.1,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyA,0x04)
keyS=ttk.Button(keyFrame,text="S")
keyS.place(relx=0.15,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyS,0x16)
keyD=ttk.Button(keyFrame,text="D")
keyD.place(relx=0.2,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyD,0x07)
keyF=ttk.Button(keyFrame,text="F")
keyF.place(relx=0.25,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyF,0x09)
keyG=ttk.Button(keyFrame,text="G")
keyG.place(relx=0.3,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyG,0x0a)
keyH=ttk.Button(keyFrame,text="H")
keyH.place(relx=0.35,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyH,0x0b)
keyJ=ttk.Button(keyFrame,text="J")
keyJ.place(relx=0.4,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyJ,0x0d)
keyK=ttk.Button(keyFrame,text="K")
keyK.place(relx=0.45,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyK,0x0e)
keyL=ttk.Button(keyFrame,text="L")
keyL.place(relx=0.5,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyL,0x0f)
keySemicolon=ttk.Button(keyFrame,text=":\n;")
keySemicolon.place(relx=0.55,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keySemicolon,0x33)
keyApostrophe=ttk.Button(keyFrame,text="\"\n\'")
keyApostrophe.place(relx=0.6,rely=0.55,relwidth=0.05,relheight=0.15)
bindButton(keyApostrophe,0x34)
keyEnter=ttk.Button(keyFrame,text="Enter")
keyEnter.place(relx=0.65,rely=0.55,relwidth=0.1,relheight=0.15)
bindButton(keyEnter,0x28)
#Line5
keyLShift=ttk.Button(keyFrame,text="Shift",command=lambda :pressCont(6,-1))
keyLShift.place(relx=0,rely=0.7,relwidth=0.125,relheight=0.15)
keyZ=ttk.Button(keyFrame,text="Z")
keyZ.place(relx=0.125,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyZ,0x1d)
keyX=ttk.Button(keyFrame,text="X")
keyX.place(relx=0.175,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyX,0x1b)
keyC=ttk.Button(keyFrame,text="C")
keyC.place(relx=0.225,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyC,0x06)
keyV=ttk.Button(keyFrame,text="V")
keyV.place(relx=0.275,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyV,0x19)
keyB=ttk.Button(keyFrame,text="B")
keyB.place(relx=0.325,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyB,0x05)
keyN=ttk.Button(keyFrame,text="N")
keyN.place(relx=0.375,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyN,0x11)
keyM=ttk.Button(keyFrame,text="M")
keyM.place(relx=0.425,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyM,0x10)
keyComma=ttk.Button(keyFrame,text="<\n,")
keyComma.place(relx=0.475,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyComma,0x36)
keyPeriod=ttk.Button(keyFrame,text=">\n.")
keyPeriod.place(relx=0.525,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyPeriod,0x37)
keySlash=ttk.Button(keyFrame,text="?\n/")
keySlash.place(relx=0.575,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keySlash,0x38)
keyRShift=ttk.Button(keyFrame,text="Shift",command=lambda :pressCont(2,-1))
keyRShift.place(relx=0.625,rely=0.7,relwidth=0.125,relheight=0.15)
#Line6
keyLCtrl=ttk.Button(keyFrame,text="Ctrl",command=lambda :pressCont(7,-1))
keyLCtrl.place(relx=0,rely=0.85,relwidth=0.1,relheight=0.15)
keyLWin=ttk.Button(keyFrame,text="Win",command=lambda :pressCont(4,-1))
keyLWin.place(relx=0.1,rely=0.85,relwidth=0.05,relheight=0.15)
keyLAlt=ttk.Button(keyFrame,text="Alt",command=lambda :pressCont(5,-1))
keyLAlt.place(relx=0.15,rely=0.85,relwidth=0.05,relheight=0.15)
keySpace=ttk.Button(keyFrame,text="")
keySpace.place(relx=0.2,rely=0.85,relwidth=0.35,relheight=0.15)
bindButton(keySpace,0x2c)
keyMenu=ttk.Button(keyFrame,text="Menu")
keyMenu.place(relx=0.55,rely=0.85,relwidth=0.05,relheight=0.15)
bindButton(keySpace,0x65)
keyRAlt=ttk.Button(keyFrame,text="Alt",command=lambda :pressCont(1,-1))
keyRAlt.place(relx=0.6,rely=0.85,relwidth=0.05,relheight=0.15)
keyRWin=ttk.Button(keyFrame,text="Win",command=lambda :pressCont(0,-1))
keyRWin.place(relx=0.65,rely=0.85,relwidth=0.05,relheight=0.15)
keyRCtrl=ttk.Button(keyFrame,text="Ctrl",command=lambda :pressCont(3,-1))
keyRCtrl.place(relx=0.7,rely=0.85,relwidth=0.05,relheight=0.15)
#Function Keys
keyPrint=ttk.Button(keyFrame,text="Print\nScreen")
keyPrint.place(relx=0.75,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyPrint,0x46)
keyScrollLock=ttk.Button(keyFrame,text="Scroll\nLock")
keyScrollLock.place(relx=0.8,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyScrollLock,0x47)
keyPauseBreak=ttk.Button(keyFrame,text="Pause\nBreak")
keyPauseBreak.place(relx=0.85,rely=0.1,relwidth=0.05,relheight=0.15)
bindButton(keyPauseBreak,0x48)

keyInsert=ttk.Button(keyFrame,text="Insert")
keyInsert.place(relx=0.75,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(keyInsert,0x49)
keyDelete=ttk.Button(keyFrame,text="Delete")
keyDelete.place(relx=0.75,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyDelete,0x4c)
keyHome=ttk.Button(keyFrame,text="Home")
keyHome.place(relx=0.8,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(keyHome,0x4a)
keyEnd=ttk.Button(keyFrame,text="End")
keyEnd.place(relx=0.8,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyEnd,0x4d)
keyPageUp=ttk.Button(keyFrame,text="Page\nUp")
keyPageUp.place(relx=0.85,rely=0.25,relwidth=0.05,relheight=0.15)
bindButton(keyPageUp,0x4b)
keyPageDown=ttk.Button(keyFrame,text="Page\nDown")
keyPageDown.place(relx=0.85,rely=0.4,relwidth=0.05,relheight=0.15)
bindButton(keyPageDown,0x4e)
keyDpadUp=ttk.Button(keyFrame,text="^")
keyDpadUp.place(relx=0.8,rely=0.7,relwidth=0.05,relheight=0.15)
bindButton(keyDpadUp,0x52)
keyDpadDown=ttk.Button(keyFrame,text="v")
keyDpadDown.place(relx=0.8,rely=0.85,relwidth=0.05,relheight=0.15)
bindButton(keyDpadDown,0x51)
keyDpadLeft=ttk.Button(keyFrame,text="<")
keyDpadLeft.place(relx=0.75,rely=0.85,relwidth=0.05,relheight=0.15)
bindButton(keyDpadLeft,0x50)
keyDpadRight=ttk.Button(keyFrame,text=">")
keyDpadRight.place(relx=0.85,rely=0.85,relwidth=0.05,relheight=0.15)
bindButton(keyDpadRight,0x4f)

listButtonCtrl=[keyRWin,keyRAlt,keyRShift,keyRCtrl,keyLWin,keyLAlt,keyLShift,keyLCtrl]
dictButtonsNormal=dict({
    0x29:keyEsc,#Esc
    0x3a:keyF1,#F1
    0x3b:keyF2,#F2
    0x3c:keyF3,#F3
    0x3d:keyF4,#F4
    0x3e:keyF5,#F5
    0x3f:keyF6,#F6
    0x40:keyF7,#F7
    0x41:keyF8,#F8
    0x42:keyF9,#F9
    0x43:keyF10,#F10
    0x44:keyF11,#F11
    0x45:keyF12,#F12
    0x46:keyPrint,#Print
    0x47:keyScrollLock,#ScrollLock
    0x48:keyPauseBreak,#PauseBreak
    0x35:keyGrave,#'
    0x1e:key1,#1
    0x1f:key2,#2
    0x20:key3,#3
    0x21:key4,#4
    0x22:key5,#5
    0x23:key6,#6
    0x24:key7,#7
    0x25:key8,#8
    0x26:key9,#9
    0x27:key0,#0
    0x2d:keyMinus,#-
    0x2e:keyEquals,#=
    0x2a:keyBackspace,#Backspace
    0x2b:keyTab,#Tab
    0x14:keyQ,#q
    0x1a:keyW,#w
    0x08:keyE,#e
    0x15:keyR,#r
    0x17:keyT,#t
    0x1c:keyY,#y
    0x18:keyU,#u
    0x0c:keyI,#i
    0x12:keyO,#o
    0x13:keyP,#p
    0x2f:keyLBracket,#[
    0x30:keyRBracket,#]
    0x31:keyBackslash,#\
    0x04:keyA,#a
    0x16:keyS,#s
    0x07:keyD,#d
    0x09:keyF,#f
    0x0a:keyG,#g
    0x0b:keyH,#h
    0x0d:keyJ,#j
    0x0e:keyK,#k
    0x0f:keyL,#l
    0x33:keySemicolon,#;
    0x34:keyApostrophe,#'
    0x28:keyEnter,#Enter
    0x1d:keyZ,#z
    0x1b:keyX,#x
    0x06:keyC,#c
    0x19:keyV,#v
    0x05:keyB,#b
    0x11:keyN,#n
    0x10:keyM,#m
    0x36:keyComma,#,
    0x37:keyPeriod,#.
    0x38:keySlash,#/
    0x2c:keySpace,#Space
    0x65:keyMenu,#Menu
    0x49:keyInsert,#Insert
    0x4c:keyDelete,#Delete
    0x4a:keyHome,#Home
    0x4d:keyEnd,#End
    0x4b:keyPageUp,#PageUp
    0x4e:keyPageDown,#PageDown
    0x50:keyDpadLeft,#Left
    0x52:keyDpadUp,#Up
    0x4f:keyDpadRight,#Right
    0x51:keyDpadDown,#Down
    })

#Keys End

sizeGrip=ttk.Sizegrip(root)
sizeGrip.place(relx=1,rely=1,anchor="se")

root.bind("<Key>", pressCapture)
root.bind("<KeyRelease>", releaseCapture)

refreshPorts()
root.mainloop()