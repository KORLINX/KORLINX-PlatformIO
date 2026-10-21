#include <Arduino.h>
#ifdef USE_TINYUSB
#include <Adafruit_TinyUSB.h>  // required for Serial when USE_TINYUSB is set
#endif

// Reads lines from Serial and sends them back. Serial is the NX40's own USB
// port, or the NX15's on-board USB-UART at 115200 baud.

String line;

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);  // the NX40's USB serial port opens with the monitor
  Serial.println("Type a line and press Enter");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c != '\r' && c != '\n') {
      line += c;
    } else if (line.length() > 0) {
      Serial.print("You typed: ");
      Serial.println(line);
      line = "";
    }
  }
}
