#include <Arduino.h>
#include <Adafruit_TinyUSB.h>  // required for Serial when USE_TINYUSB is set

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  Serial.printf("NX40 up, BSP %s, %.2f\n", ARDUINO_BSP_VERSION, 3.14f);
}

void loop() {
  Serial.println(millis());
  delay(1000);
}
