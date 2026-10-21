#include <Arduino.h>

// Fades the red LED in and out. On the NX15 red is the only LED on a PWM
// channel (PWM20); there analogWrite() on the other LEDs can only turn them
// on or off.

int brightness = 0;
int step = 5;

void setup() {
}

void loop() {
  analogWrite(LED_RED, brightness);
  brightness += step;
  if (brightness <= 0 || brightness >= 255) {
    step = -step;
  }
  delay(30);
}
