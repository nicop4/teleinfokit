#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#if _HW_VER <= 4
  #include <ESP8266WiFi.h>
  #include <TZ.h>
  #define OLED_SDA_PIN 0
  #define OLED_SCL_PIN 2
#elif _HW_VER == 5
  #include <WiFi.h>
  #include "TZ_ESP32.h"
  #define OLED_SDA_PIN 8
  #define OLED_SCL_PIN 9
#elif _HW_VER == 6
  #include <WiFi.h>
  #include "TZ_ESP32.h" // use the same as HW5
  #define OLED_SDA_PIN 14
  #define OLED_SCL_PIN 15
#endif

#include <Wire.h>
#include "qrcode.h"
#include "SSD1306Wire.h"
#include "data.h"
#include "version.h"
#include "fonts.h"

#define HEIGHT 32
#define WIDTH 128

#define DISPLAY_STEP_MS 2000

class Display
{
public:
    Display();
    time_t now;

    char buffer[80];

    void init(Data *d);
    void loop(void);
    void log(String text, int16_t displayTime = 500);
    void logPercent(String text, int percentage);
    void displayAPData(String ssid, String password);
    void drawGraph(long papp, char mode);
    void displayData1(long papp, long iinst);
    void displayData2(long index, char *compteur);
    void displayNetwork();
    void displayTime();
    void displayReset(String apKey);
    void displayOff();
    void displayStartup(String version);
    void displayTestTic(String power, String index, char ticMode);
    void getTime();

private:
    Data *data;
    uint8_t displayGraphStep;
    unsigned long lastGraphStepUpdate;
}; 

#endif /* DISPLAY_H */
