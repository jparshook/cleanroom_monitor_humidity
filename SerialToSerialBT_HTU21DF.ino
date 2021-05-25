//This example code is in the Public Domain (or CC0 licensed, at your option.)
//By Evandro Copercini - 2018
//
//This example creates a bridge between Serial and Classical Bluetooth (SPP)
//and also demonstrate that SerialBT have the same functionalities of a normal Serial

#include "BluetoothSerial.h"
#include <Wire.h>
#include "Adafruit_HTU21DF.h"
#include "esp_bt_device.h"

// Connect Vin to 3-5VDC
// Connect GND to ground
// Connect SCL to I2C clock pin (A5 on UNO)
// Connect SDA to I2C data pin (A4 on UNO)

Adafruit_HTU21DF htu = Adafruit_HTU21DF();

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(9600);
  SerialBT.begin("ESP32_Sensor2"); //Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
  
  Serial.println("HTU21D-F test");
  if (!htu.begin()) {
    Serial.println("Couldn't find sensor!");
    while (1);
    }
}

void loop() {

  String MAC_addr;
  const uint8_t* point = esp_bt_dev_get_address();
  for (int i = 0; i < 6; i++) {
    char str[3];
    sprintf(str, "%02X", (int)point[i]);
    MAC_addr += str;
    if (i < 5){
      MAC_addr += ":";
    }
  }

  float temp = htu.readTemperature();
  float rel_hum = htu.readHumidity();

//  float temp = 20;
//  float rel_hum = 20;
  
//  String res_str = "24:0A:C4:0C:16:DA";

  String res_str = MAC_addr;
  res_str += ",";
  res_str += String(temp, 2);
  res_str += ",";
  res_str += String(rel_hum, 2);
  res_str += "\n";
  
  SerialBT.write((uint8_t*)(res_str.c_str()), res_str.length());
  Serial.print(res_str);
  
   //Serial.print("Sending: ");
   //Serial.print(SerialBT.write((uint8_t*)(res_str.c_str()), res_str.length()));
   //Serial.print(" bytes.\n");
    
  delay(1000*30);
}
