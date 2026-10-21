#include <Arduino.h>
#include <Wire.h>
#ifdef USE_TINYUSB
#include <Adafruit_TinyUSB.h>  // required for Serial when USE_TINYUSB is set
#endif

// Reads temperature and humidity from the on-board SHTC3 on Wire, every
// two seconds. Each reply word from the SHTC3 is followed by a CRC-8.

#define SHTC3_ADDR    0x70
#define SHTC3_WAKEUP  0x3517
#define SHTC3_SLEEP   0xB098
#define SHTC3_READ_ID 0xEFC8
#define SHTC3_MEASURE 0x7866  // normal mode, temperature first, no clock stretching

bool shtc3Command(uint16_t command) {
  Wire.beginTransmission(SHTC3_ADDR);
  Wire.write(command >> 8);
  Wire.write(command & 0xFF);
  return Wire.endTransmission() == 0;
}

bool shtc3Read(uint16_t *words, size_t count) {
  if (Wire.requestFrom(SHTC3_ADDR, count * 3) != count * 3) {
    return false;
  }
  for (size_t i = 0; i < count; i++) {
    uint8_t data[2] = {(uint8_t)Wire.read(), (uint8_t)Wire.read()};
    uint8_t crc = 0xFF;
    for (uint8_t byte : data) {
      crc ^= byte;
      for (int bit = 0; bit < 8; bit++) {
        crc = crc & 0x80 ? (crc << 1) ^ 0x31 : crc << 1;
      }
    }
    if (crc != Wire.read()) {
      return false;
    }
    words[i] = data[0] << 8 | data[1];
  }
  return true;
}

// The SHTC3 sleeps between measurements and needs a wake-up before any
// other command
bool shtc3Wake() {
  bool ok = shtc3Command(SHTC3_WAKEUP);
  delayMicroseconds(240);
  return ok;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);  // the NX40's USB serial port opens with the monitor
  Wire.begin();

  uint16_t id;
  bool found = shtc3Wake() && shtc3Command(SHTC3_READ_ID) && shtc3Read(&id, 1)
               && (id & 0x083F) == 0x0807;
  shtc3Command(SHTC3_SLEEP);
  Serial.println(found ? "SHTC3 found" : "SHTC3 not found");
}

void loop() {
  uint16_t raw[2];
  bool ok = shtc3Wake() && shtc3Command(SHTC3_MEASURE);
  if (ok) {
    delay(13);  // 12.1 ms at most in normal mode
    ok = shtc3Read(raw, 2);
  }
  shtc3Command(SHTC3_SLEEP);

  if (ok) {
    Serial.print(-45 + 175 * raw[0] / 65536.0f, 2);
    Serial.print(" C  ");
    Serial.print(100 * raw[1] / 65536.0f, 1);
    Serial.println(" %RH");
  } else {
    Serial.println("SHTC3 read failed");
  }
  delay(2000);
}
