#include <Arduino.h>

// Lights the four LEDs of the DK in turn

const int leds[] = {LED_RED, LED_GREEN, LED_BLUE, LED_RUN};

void setup() {
  for (int led : leds) {
    pinMode(led, OUTPUT);
    digitalWrite(led, !LED_STATE_ON);
  }
}

void loop() {
  for (int led : leds) {
    digitalWrite(led, LED_STATE_ON);
    delay(300);
    digitalWrite(led, !LED_STATE_ON);
  }
}
