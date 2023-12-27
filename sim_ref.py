# *** dwnld 29-03-2023
# *** updated button for get tags
## rework added

import random
import time
import math
import os
from datetime import datetime
import pandas as pd
from tkinter import *
from tkinter import filedialog
from opcua import Client, ua

c_path = os.getcwd()
deviation_range = 0.2
link = c_path + '/config.csv'
dfc = pd.read_csv(link)
tags = {}
pyserver = 0
Tool1, Tool2, Tool3, Tool4 = 0, 0, 0, 0

initial_setup = True

for i in range(0, dfc.shape[0]):
    tags[str(dfc.loc[i, "TAG"])] = str(dfc.loc[i, "ID"])
station = tags["Machine_name"]


# check connection
def connect_opcua():
    global client, com
    try:
        com = "ns=4;i="
        client = Client("opc.tcp://" + str(tags['ip']) + ":4840")
        client.connect()
        print("Client connected for server IP: {IP} & Port: 4840".format(IP=str(tags['ip'])))
    except:
        print("Couldn't connect to server IP :{IP} & Port: 4840".format(IP=str(tags['ip'])))


connect_opcua()

bcg = "#002e62"
fc = "#8c92ac"
root = Tk()
root.geometry('280x390')
root.title(station)
root.configure(bg=bcg)
root.iconbitmap("ICON.ico")
i = 1
flag = False
Diag = True

old_minute, minute, ok, nok = 0, 0, 0, 0
sim_minute = []
columns = []
csv_ok = True
Sim_start = False
Data_instance = {}

OK, NOK, REWORK, TOTAL, CC = 0, 0, 0, 0, 0


# Csv correctness

def order(sim_minute):  # Ascending order
    for i in range(len(sim_minute) - 1):
        if sim_minute[i] - sim_minute[i + 1] > 0:
            return False
    return True


def checkfile(path):
    global df, csv_ok
    if ((path.split('/'))[-1].split('.')[-1]) == 'csv':
        df = pd.read_csv(path)
        max_row = df.shape[0]
        for i in df.columns:
            columns.append(i)
        if Diag: print("Columns : ", columns)
        for i in range(max_row):
            q = df.loc[i, "Minute"]
            sim_minute.append(int(q))

        if len(sim_minute) != len(set(sim_minute)):
            print("SIM_CD Time having duplicate values !")
            checkfilel.configure(text="Duplicate Time Detected")
            csv_ok = False
        else:
            checkfilel.configure(text="Time line not in Ascending")
            csv_ok = order(sim_minute)

    else:
        csv_ok = False
        checkfilel.configure(text="Wrong File Extension !")
    if csv_ok:
        checkfilel.configure(text="File Ready to simulation")
        min = df.loc[int(df.shape[0]) - 1, 'Minute']
        noofvar = len(df['Variant'].unique())
        Variant = Label(text="Variant Detected: " + str(noofvar), bg=bcg, fg=fc, font=("Berlin Sans FB", 12,))
        Variant.place(x=10, y=150)

        Total_sim_min = Label(text="Total Simulation minutes : " + str(min), bg=bcg, fg=fc,
                              font=("Berlin Sans FB", 12,))
        Total_sim_min.place(x=10, y=175)


# csv correctness check ends


def print_tags():
    print(tags)


# server connection checking starts

def sendata(tagname, tagvalue):
    if pyserver == 0:
        try:
            # print(com + tags[tagname])
            Temp = client.get_node(com + tags[tagname])
            dv = ua.DataValue(ua.Variant(tagvalue, ua.VariantType.Int32))
            Temp.set_value(dv)
        except:
            print("check server url/nodeid for" + tagname)
    else:
        print("python as a server Int")


def sendbool(tagname, tagvalue):
    if pyserver == 0:
        try:
            Temp = client.get_node(com + tags[tagname])
            dv = ua.DataValue(ua.Variant(tagvalue, ua.VariantType.Boolean))
            Temp.set_value(dv)
        except:
            print("check server url/nodeid for" + tagname)
    else:
        print("python as a server Bool")


def sendfloat(tagname, tagvalue):
    if pyserver == 0:
        try:
            # print(com + tags[tagname])
            Temp = client.get_node(com + tags[tagname])
            dv = ua.DataValue(ua.Variant(tagvalue, ua.VariantType.Float))
            Temp.set_value(dv)
        except:
            print("check server url/node id for" + tagname)
    else:
        print("python as a server float")


def check_conn():
    ran = random.randint(1, 119)
    print(ran)
    try:
        Temp = client.get_node(com + tags["pycomm"])
        dv = ua.DataValue(ua.Variant(ran, ua.VariantType.Int32))
        Temp.set_value(dv)
        Temperature = Temp.get_value()

        if ran == Temperature:
            print("connection ok")
            text = "last checked on "
            Label(text=text + (str(datetime.now())).split('.')[0], bg=bcg, fg=fc, font=("Berlin Sans FB", 10)).place(
                x=10, y=274)
            con_stat.configure(text="Healthy", bg=bcg, fg='green', font=("Berlin Sans FB", 10))
    except:
        text = "last checked on "
        Label(text=text + (str(datetime.now())).split('.')[0], bg=bcg, fg=fc, font=("Berlin Sans FB", 10)).place(x=10,
                                                                                                                 y=274)
        con_stat.configure(text="Not Healthy", bg=bcg, fg='red', font=("Berlin Sans FB", 10))
        Button(text="", width=1, height=1, command=connect_opcua, borderwidth=0).place(x=215, y=10)


# server connection checking ends

def error_active(txt):
    ea = []
    # print(txt , type(txt))
    if txt != '0':

        alms = txt.split(":")
        for i in alms:
            if i.isnumeric() and int(i) < 16:
                ea.append(i)
            else:
                print("format issue")

        error_active = list('0000000000000000')
        for j in ea:
            for i in range(1, 17):
                if i == int(j):
                    error_active[int(i - 1)] = '1'
        error_bit = int(''.join(error_active[::-1]), 2)

        print(datetime.now(), "Error Active !!   I/P Alms :", alms, "Error generated :", ea, "binary fromat :",
              error_bit)
        ea.clear()
        return error_bit

    else:
        default16 = 32768
        print(datetime.now(), "No Error configured , default error 16 will triggered.  binary code :32768")
        return default16


CurrRejNo = 0


# Actual Simulation Starts here


def Run_Machine():
    global old_minute, minute, ok, Sim_start, lasttime, OK, NOK, REWORK, TOTAL, CC, CurrRejNo, initial_setup, Tool1, Tool2, Tool3, Tool4

    RejReasons = [101, 102, 103, 104]
    if Sim_start:
        if initial_setup:
            try:
                tool1_tag = client.get_node(com + tags["tool1"])
                Tool1 = tool1_tag.get_value()
                tool2_tag = client.get_node(com + tags["tool2"])
                Tool2 = tool2_tag.get_value()
                tool3_tag = client.get_node(com + tags["tool3"])
                Tool3 = tool3_tag.get_value()
                print(" >>> Tool date read from gateway", Tool1, Tool2, Tool3)
            except:
                print(" >>> Couldn't read tool data from gateway")

            lasttime = datetime.now()
            initial_setup = False
        c_time = datetime.now()
        c_minute = ((str(datetime.now()).split(' ')[1]).split('.')[0]).split(':')[1]
        if c_minute != old_minute:
            minute = minute + 1
            # ------------------------------------------------------------------------------------------------------------------------------------
            if minute in sim_minute:
                index = sim_minute.index(minute)
                print("Current minute :", index)
                for i in columns:
                    Data_instance[i] = df.loc[index, i]

                print("||", Data_instance)
            # ---------------------------------------------------------------------------------------------------------------

            old_minute = c_minute
        rejcode = []
        diff = datetime.now() - lasttime

        if diff.total_seconds() >= Data_instance['CT']:
            lasttime = datetime.now()

            print('---------------------------------------------------------------------------------------------------')
            sendbool("as", bool(Data_instance['AS']))
            sendbool("ar", bool(Data_instance['AR']))
            sendbool("mm", bool(Data_instance['MM']))
            sendbool("ea", bool(Data_instance['EA']))
            sendata("Variant", Data_instance['Variant'])
            for x in range(Data_instance['NOF']):
                sendata("Rfix" + str(x + 1), 0)

            if Data_instance['AR'] == 1 and Data_instance['AS'] == 1 and Data_instance['EA'] == 0 and Data_instance[
                'MM'] == 0:
                sendata("err_w1", 0)

                if Data_instance['RC'] <= Data_instance['NOF']:  # sequence start
                    CC = CC + 1

                    if CC == Data_instance['RF']:
                        OK = OK + (Data_instance['NOF'] - Data_instance['RC'])
                        if Data_instance['rework'] == 1 :
                            if (NOK-REWORK)>Data_instance['NOF']:
                                REWORK = REWORK + (Data_instance['NOF'] - Data_instance['RC'])
                            else:
                                print(" no nok parts to rework , normal sequence executing")

                        NOK = NOK + Data_instance['RC']
                        for l in range(Data_instance['RC']):
                            rejcode.append(RejReasons[CurrRejNo])
                            sendata("Rfix" + str(l + 1), RejReasons[CurrRejNo])
                            CurrRejNo = CurrRejNo + 1 if CurrRejNo < (len(RejReasons) - 1) else 0
                        CC = 0
                    else:
                        if Data_instance['rework'] == 1 :
                            if (NOK-REWORK)>Data_instance['NOF']:
                                REWORK = REWORK + Data_instance['NOF']
                            else:
                                print(" no nok parts to rework , normal sequence executing")
                        OK = OK + Data_instance['NOF']

                    # rework start
                    # print("here", Data_instance['rework'])
                    if NOK <= int(Data_instance['NOF']):
                        pass

                    # rework stop
                    cycle_time = round(diff.total_seconds() + random.uniform(0, deviation_range), 2)
                    Tool1 = Tool1 + 2
                    Tool2 = Tool2 + 2
                    Tool3 = Tool3 + 1
                    Tool4 = Tool4 + 1

                    print(datetime.now(), "variant:", Data_instance['Variant'], " ", "OK: ", OK, " NOK: ", NOK, rejcode,
                          "REWORK:", REWORK, "CT: ", cycle_time, " Tool1:", Tool1, " Tool2:", Tool2, " Tool3:", Tool3)
                    sendata("ok", OK)
                    sendata("nok", NOK)
                    sendata("rework" , REWORK)
                    sendfloat("ct", round(diff.total_seconds() + random.uniform(0, deviation_range), 2))
                    sendata("tool1", Tool1)
                    sendata("tool2", Tool2)
                    sendata("tool3", Tool3)

                else:
                    print("No of fixtures less than no of rejections , check config")

            elif Data_instance['AR'] == 0 and Data_instance['AS'] == 1 and Data_instance['EA'] == 0 and Data_instance[
                'MM'] == 0:
                print("As selected")


            elif Data_instance['EA'] == 1:
                txt = Data_instance['EB']
                error_bit = error_active(txt)
                sendata("err_w1", error_bit)

            elif Data_instance['AR'] == 0 and Data_instance['AS'] == 0 and Data_instance['EA'] == 0 and Data_instance[
                'MM'] == 1:
                print("manual mode !!")

    root.after(1, Run_Machine)


def tyu():
    global Sim_start, flag, csv_ok
    print(csv_ok)
    if flag and csv_ok:
        Sim_start = False
        flag = False
        start.configure(text='Pause here', command=tyu, font=("Berlin Sans FB", 19,), width=20, height=1,
                        cursor='dotbox')
    elif csv_ok:
        Sim_start = True
        flag = True
        start.configure(text='Resume here', command=tyu, font=("Berlin Sans FB", 19,), width=20, height=1,
                        cursor='dotbox')


def test():
    print("ok")
    text = "Last checked at "
    Label(text=text + (str(datetime.now())).split('.')[0], bg=bcg, fg=fc, font=("Berlin Sans FB", 10)).place(x=10,
                                                                                                             y=274)

    Label(text='Healthy !', bg=bcg, fg=fc, font=("Berlin Sans FB", 13)).place(x=50, y=248)


def upload():
    global link
    filename = filedialog.askopenfilename(initialdir="/",
                                          title="Select a File",
                                          filetypes=(("Text files",
                                                      "*.txt*"),
                                                     ("all files",
                                                      "*.*")))
    link = filename
    path.configure(text=(filename.split('/')[-1]))
    checkfile(link)


Font_tuple = ("Berlin Sans FB", 14,)
click_btn = PhotoImage(file=c_path + '\csv.jpg')

imgpath = c_path + '\ss.png'
img = PhotoImage(file=imgpath)
img = img.zoom(25)  # with 250, I ended up running out of memory
img = img.subsample(95)  # mechanically, here it is adjusted to 32 instead of 320
panel = Label(root, image=img)

Label(text="Machine Data Simulator", bg=bcg, fg=fc, font=Font_tuple).place(x=10, y=10)
path = Label(text="File not selected", bg=bcg, fg=fc, font=("Berlin Sans FB", 12,))
path.place(x=85, y=58)
checkfilel = Label(text=" ", bg=bcg, fg=fc, font=("Berlin Sans FB", 12,))
checkfilel.place(x=85, y=83)

Button(text='Check gateway conn', command=check_conn, ).place(x=10, y=248)

start = Button(text='Start Simulation', command=tyu, font=("Berlin Sans FB", 19,), width=20, height=1, cursor='dotbox')
start.place(x=0, y=300)
Button(image=img, command=upload, width=50, height=50).place(x=25, y=55)
Label(text=station, bg=bcg, fg='white', font=Font_tuple).place(x=5, y=355)

Button(text="View Tag list", width=11, height=1, command=print_tags).place(x=10, y=120)
con_stat = Label(text="-", bg=bcg, font=("Berlin Sans FB", 10))
con_stat.place(x=138, y=250)

root.after(1, Run_Machine)

root.mainloop()
