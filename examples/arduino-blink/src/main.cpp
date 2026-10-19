#include <Arduino.h>

bool on;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  on = !on;
  digitalWrite(LED_BUILTIN, on);
  delay(500);
}
