#include <Arduino.h>
#ifdef USE_TINYUSB
#include <Adafruit_TinyUSB.h>  // required for Serial when USE_TINYUSB is set
#endif

// Counts presses of the button (SW2 on the NX40) and lights the blue LED
// while it is held. The button is active low.

int lastState = HIGH;
unsigned long lastChange;
int presses;

void setup() {
  pinMode(PIN_BUTTON1, INPUT_PULLUP);
  pinMode(LED_BLUE, OUTPUT);
  digitalWrite(LED_BLUE, !LED_STATE_ON);
  Serial.begin(115200);
  while (!Serial) delay(10);  // the NX40's USB serial port opens with the monitor
  Serial.println("Press the button");
}

void loop() {
  int state = digitalRead(PIN_BUTTON1);
  // after a change, ignore the contact bounce for 20 ms
  if (state != lastState && millis() - lastChange >= 20) {
    lastState = state;
    lastChange = millis();
    digitalWrite(LED_BLUE, state == LOW ? LED_STATE_ON : !LED_STATE_ON);
    if (state == LOW) {
      Serial.print("Pressed ");
      Serial.println(++presses);
    }
  }
}
