#!/usr/bin/python3
import asyncio
import time
from time import localtime, strftime
import threading
import serial #pip3 install pyserial
import subprocess
import sys
import os
from datetime import date
import zipfile

def connect_to_sensor():                                    # function to connect RPi bluetooth to sensors via rfcomm channels
    subproc1 = subprocess.Popen("sudo rfcomm release all", shell=True)  # forces all rfcomm connections to disconnected
    time.sleep(5)                                                       # 5-second delay
    subproc1.kill()
    rfcomm_num = 0                                          # initialize rfcomm channel to 0
    MAC_addrs = ["24:62:AB:FD:6A:AA","24:62:AB:FC:98:06"]   # list of ESP32 MAC addresses
    sers = []                                               # create a blank list for storing serial connections
    for MAC_addr in MAC_addrs:                              # repeat these steps for each MAC address
        subproc = subprocess.Popen("sudo rfcomm connect " + str(rfcomm_num) + " " + MAC_addr + " 1", shell=True)    # runs commands via terminal
        time.sleep(3)                                       # delays the program by 3 seconds
        subproc.kill()                                      # forces subproc to stop, otherwise rfcomm connections will not be completed
        sers.append(serial.Serial(                          # create an instance for each serial connection and append to sers list
        port='/dev/rfcomm' + str(rfcomm_num),               # each MAC address has its own rfcomm channel
        baudrate = 115200,                                   # This should match what is in the sensor's Arduino sketch.
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    ))
        rfcomm_num += 1                                     # increment for the next MAC address
    return(sers)                                            # return list of serial connections for other functions to access

def new_zip_file(path):					# this function zips old sensor data
    datanum = 28800 #lines to cut
    with open(path, "r") as file_obj:
        data = file_obj.read().split("\n")
        olddata = data[:datanum]
        keepdata = data[datanum:]
        file_obj.close()
    os.remove(path)
    with open(path, "a") as file_obj:
        for line in keepdata:
            file_obj.write(line+"\n")
        file_obj.close()
    with open(path+"_archive_"+str(date.today())+".txt","w") as file_obj:
        for line in olddata:
            file_obj.write(line+"\n")
        file_obj.close()
    with zipfile.ZipFile(path+str(date.today())+".zip", "w") as myzip:
        myzip.write(path+"_archive_"+str(date.today())+".txt")
        os.remove(path+"_archive_"+str(date.today())+".txt")

def read_from_sensor(ser):                                                      #  this function retrieves the sensor readings and stores them in a file per MAC address
    while True:
        try:                                                                    # error handling to catch if a sensor is momentarily disconnected
            sensor_data = ser.readline().decode('utf-8')                        # store incoming sensor data to variable
            sensor_data = sensor_data.split(',')                                # separate the data on each comma and store in a list
            sensor_name = sensor_data[0]                                        # extract MAC address to save to .txt file
            sensor_data[0] = strftime("%d %b %Y, %H:%M:%S", localtime())         # replace MAC address with timestamp
            sensor_data = ', '.join(sensor_data)                                # convert back to string
            print(sensor_data)                                                  # for troubleshooting purposes only, can be deleted
            with open('/home/pi/Documents/sensors_project/'+ sensor_name + '.txt', 'a') as file_obj:        # change file path as needed
                file_obj.write(sensor_data)                # writes sensor data to a txt file on the RPi

            if sensor_name == "24:62:AB:FC:98:06":
                with open('/var/www/html/dryboxsensordata.txt', 'a') as file_obj:         # added by amy to connect with website
                    file_obj.write(sensor_data)
                with open('/var/www/html/dryboxsensordata.txt', 'r') as f:
                    if len(f.read().split("\n"))>28900: new_zip_file('/var/www/html/dryboxsensordata.txt')
            if sensor_name == "24:62:AB:FD:6A:AA":
                with open('/var/www/html/ambientsensordata.txt', 'a') as file_obj:         # added by amy to connect with website
                    file_obj.write(sensor_data)
                with open('/var/www/html/ambientsensordata.txt', 'r') as f:
                    if len(f.read().split("\n"))>28900: new_zip_file('/var/www/html/ambientsensordata.txt')
        except:                                                                 # if an error is detected (i.e. lost connection to board)
            subproc1 = subprocess.Popen("sudo rfcomm release all", shell=True)  # forces all rfcomm connections to disconnected
            time.sleep(5)                                                       # 5-second delay
            subproc1.kill()                                                     # force subproc1 to end to move on
            python = sys.executable                                             # controls execution of this python script
            os.execl(python, python, * sys.argv)                                # restarts this python script


async def main(*s):
    await asyncio.gather(read_from_sensor(ser) for sers in s)


if __name__ == '__main__':
    time.sleep(10)             # this file is listed in /etc/rc.local to run at startup and needs a delay for other programs to initialize first
    sers = connect_to_sensor()  # connects the sensor boards to rfcomm ports

    threads = []
    for ser in sers:            # allows the RPi to read incoming data as it becomes available in no particular order
        threads.append(threading.Thread(target=read_from_sensor, args=(ser,)))
        threads[-1].start()