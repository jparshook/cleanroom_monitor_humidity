# Temperature and Humidity Monitoring

This project is specifically for an ISO 7 clean room in which electrical modules must be stored in 20% humidity. Temperature and humidity sensors are connected to ESP32 boards that send data to a central RPi. The end goal is to have this RPi make this data accessible from the Internet. In this project, Bluetooth is used. [Many similar projects use MQTT](https://diyi0t.com/introduction-into-mqtt/) which uses WiFi to transmit sensor data to the RPi instead. Bluetooth is used in this instance because offline data transmission is preferred.

## Components used for this project
- [Raspberry Pi 4 with power cable and MicroSD card w/NOOBS](https://www.canakit.com/raspberry-pi-4-starter-kit.html)
- [ESP32 boards](https://www.amazon.com/DORHEA-Development-NodeMCU-32S-Microcontroller-Integrated/dp/B086MGH7JV/)
- USB to mini cable for each ESP32 board
- [humidity and temperature sensors](https://www.adafruit.com/product/3515)
- [jumper wires](https://www.amazon.com/EDGELEC-Breadboard-Optional-Assorted-Multicolored/dp/B07GD2BWPY/)
- PC (Windows 10) with mouse and keyboard




## ESP32 setup
[There are several ESP32 boards available](https://makeradvisor.com/esp32-development-boards-review-comparison/), and any model should work. Note that certain ESP32 boards, including ESP32 DEVKIT DOIT which is used in this project, require holding the boot button when flashing.

### Hardware setup
- Refer to the sensors user guide if available. [The HTU21D-F sensor is used in this project.](https://learn.adafruit.com/adafruit-htu21d-f-temperature-humidity-sensor/wiring-and-test)
- Refer to the [ESP32 user guide as well for the pinout](https://images-na.ssl-images-amazon.com/images/I/518Z-EBLHgL._AC_.jpg).
Connect the sensor to the ESP32 with the jumper wires according the the pinouts. A breadboard can be used here but is not necessary.
- Connect the ESP32 to the PC with the USB mini cable.
- Download and install the appropriate driver for your ESP32 USB connection. [The CP2104 USB driver was installed in this case.](http://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers)

### Arduino IDE
- [On a computer, download the appropriate Arduino installation file for the OS.](https://www.arduino.cc/en/software)
- Open Arduino IDE.
- [Follow these instructions to install the ESP32 boards in Arduino.](https://github.com/espressif/arduino-esp32/bloba/master/docs/arduino-ide/boards_manager.md)
    - In this case, select *Tools --> Board --> ESP32 Arduino --> DOIT ESP32 DEVKIT V1* for the last step. Refer to the ESP32 user guide to determine the appropriate selection.
- Go to *Tools --> Port* and select the appropriate port for the USB connection.
    - If the port is uncertain, open Device Manager. The port associated with *Silicon Labs CP210x* is the correct port.
- Go to *Tools --> Manage Libraries...*
- Search for *Adafruit HTU21DF* and install.
- Open this project's ino file in Arduino.
- Change the last line of code to change the frequency of the sensor readings as needed.
    - ```delay(1000*30);``` takes measurements every 30 seconds.
- Click on the serial monitor (magnifying glass) with the baud rate of 9600.
    - In general, this number should match the value in ```Serial.begin(value);``` 
- Upload the file to the ESP32.
    - Hold the boot button on the board until *Connecting...* appears at the bottom of the screen if needed.
- The serial monitor will flash some text to indicate if the sensor is connected or not. Sensor readings will start to appear shortly after.
- The ESP32 can now be moved from the computer to wall or battery power.

## Raspberry Pi setup
Any RPi with Bluetooth should work for this project. In this case, RPi4 was used. 

### Initial Setup
- [Install the Raspbian OS and connect to WiFi.](https://www.canakit.com/Media/CanaKit-Raspberry-Pi-Quick-Start-Guide-4.0.pdf) If WiFi is not available, use an Ethernet cable to connect to the Internet for the next step.
- From the main menu, go to *Preferences --> Raspberry Pi Configuration --> Interfaces* and enable Serial Port and SSH and save.
- At this point, the RPi can be accessed with secure shell (SSH) from another machine to make switching between this device and the ESP32 boards easier.
    - Get the IP address: ```ifconfig```
    - Restart the system to fully enable SSH: ```sudo reboot```
    - [Refer to Section 4 in this link for OS specific instructions to access the RPi remotely.](https://www.raspberrypi.org/documentation/remote-access/ssh/) 
- [Install the latest updates.](https://www.raspberrypi.org/documentation/raspbian/updating.md) Enter the following in the remote RPi secure shell:
    - ```sudo apt update```
    - ```sudo apt full-upgrade```
    - ```sudo reboot```
### Bluetooth setup
- [Create a serial port profile:](https://www.teachmemicro.com/setting-raspberry-pi-zero-bluetooth/)
    - ```sudo nano /etc/systemd/system/dbus-org.bluez.service```
    - Find this line: ```ExecStart=/usr/lib/bluetooth/bluetoothd```
        - Add ```-C``` at the end of this line
        - Directly after this line, add ```ExecStartPost=/usr/bin/sdptool add SP```
    - Ctrl+s to save and then Ctrl+x to exit.
    - Restart the system: ```sudo reboot```
- Trust and pair the ESP32:
    - ```bluetoothctl```
    - ```scan on``` - Look for the ESP32 and note the MAC address.
    - ```scan off```
    - ```pair <ESP32 MAC address>```
    - ```trust <ESP32 MAC address>```
    - ```paired-devices``` - This should show the ESP32
    - ```help``` shows a list of valid commands in bluetoothctl
    - CTRL+X to exit bluetoothctl
- Download and run serial_read.py. Verify that a txt file named after the ESP32 MAC address appears in the same directory as the Python script.
- [Set the RPi to run this file automatically at startup.](https://www.makeuseof.com/how-to-run-a-raspberry-pi-program-script-at-startup/) In this case, Method 1 was utilized in this project.
- ```sudo reboot``` - Check for new measurements 2 minutes after startup.
