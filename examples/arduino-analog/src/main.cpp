#include <Arduino.h>
#ifdef USE_TINYUSB
#include <Adafruit_TinyUSB.h>  // required for Serial when USE_TINYUSB is set
#endif

// Prints the voltage on the analog pins of the J3 header: A0-A6 on the
// NX40, A0-A4 on the NX15. Both read 0-3.6 V in 10 bits, the NX40 with gain
// 1/6 on its 0.6 V internal reference, the NX15 with gain 1/4 on 0.9 V.

#ifdef ARDUINO_NX40_NRF52840
const int inputs[] = {A0, A1, A2, A3, A4, A5, A6};
#else
const int inputs[] = {A0, A1, A2, A3, A4};
#endif

void setup() {
  Serial.begin(115200);
}

void loop() {
  for (size_t i = 0; i < sizeof(inputs) / sizeof(inputs[0]); i++) {
    Serial.print('A');
    Serial.print(i);
    Serial.print(' ');
    Serial.print(analogRead(inputs[i]) * 3600L / 1024);
    Serial.print(" mV  ");
  }
  Serial.println();
  delay(500);
}
