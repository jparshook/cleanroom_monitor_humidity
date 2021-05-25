#!/usr/bin/python3
import asyncio
import time
from time import localtime, strftime
import threading
import serial #pip3 install pyserial
import subprocess
import sys
import os


def connect_to_sensor():                                    # function to connect RPi bluetooth to sensors via rfcomm channels
    rfcomm_num = 0                                          # initialize rfcomm channel to 0
    MAC_addrs = ["24:62:AB:FB:16:02","24:0A:C4:0C:16:DA"]   # list of ESP32 MAC addresses
    sers = []                                               # create a blank list for storing serial connections
    for MAC_addr in MAC_addrs:                              # repeat these steps for each MAC address
        try:
            subproc = subprocess.Popen("sudo rfcomm connect " + str(rfcomm_num) + " " + MAC_addr + " 1", shell=True)    # runs commands via terminal
            time.sleep(3)                                       # delays the program by 3 seconds
            subproc.kill()                                      # forces subproc to stop, otherwise rfcomm connections will not be completed
            sers.append(serial.Serial(                          # create an instance for each serial connection and append to sers list
            port='/dev/rfcomm' + str(rfcomm_num),               # each MAC address has its own rfcomm channel
            baudrate = 9600,                                    # This should match what is in the sensor's Arduino sketch.
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
            ))
            rfcomm_num += 1                                     # increment for the next MAC address
        except:                                             # error handling in case that a sensor is down
            pass
    return(sers)                                            # return list of serial connections for other functions to access

def read_from_sensor(ser):                                                      #  this function retrieves the sensor readings and stores them in a file per MAC address
    while True:
        try:                                                                    # error handling to catch if a sensor is momentarily disconnected
            sensor_data = ser.readline().decode('utf-8')                        # store incoming sensor data to variable
            sensor_data = sensor_data.split(',')                                # separate the data on each comma and store in a list
            sensor_name = sensor_data[0]                                        # extract MAC address to save to .txt file
            sensor_data[0] = strftime("%d %b %Y %H:%M:%S", localtime())         # replace MAC address with timestamp
            sensor_data = ', '.join(sensor_data)                                # convert back to string
            print(sensor_data)                                                  # for troubleshooting purposes only, can be deleted
            with open('/home/pi/Documents/sensors_project/'+ sensor_name + '.txt', 'a') as file_obj:        # change file path as needed
                file_obj.write(sensor_data)                                     # writes sensor data to a txt file on the RPi
        except:                                                                 # if an error is detected (i.e. lost connection to board)
            subproc1 = subprocess.Popen("sudo rfcomm release all", shell=True)  # forces all rfcomm connections to disconnected
            time.sleep(5)                                                       # 5-second delay
            subproc1.kill()                                                     # force subproc1 to end to move on
            python = sys.executable                                             # controls execution of this python script
            os.execl(python, python, * sys.argv)                                # restarts this python script


async def main(*s):
    await asyncio.gather(read_from_sensor(ser) for sers in s)


if __name__ == '__main__':
    time.sleep(120)             # this file is listed in /etc/rc.local to run at startup and needs a delay for other programs to initialize first
    sers = connect_to_sensor()  # connects the sensor boards to rfcomm ports

    threads = []
    for ser in sers:            # allows the RPi to read incoming data as it becomes available in no particular order
        threads.append(threading.Thread(target=read_from_sensor, args=(ser,)))
        threads[-1].start()