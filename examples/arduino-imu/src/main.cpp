#include <Arduino.h>
#include <Wire.h>
#ifdef USE_TINYUSB
#include <Adafruit_TinyUSB.h>  // required for Serial when USE_TINYUSB is set
#endif

// Reads acceleration and rotation from the on-board IMU on Wire, five times
// a second. The NX40 has an LSM6DS3TR-C, the NX15 an LSM6DSL; the registers
// used here are the same on both.
//
// Wire on the NX15 sends a stop between writing the register address and
// reading; the IMU keeps the address across it.

#define IMU_ADDR     0x6A
#define IMU_WHO_AM_I 0x0F
#define IMU_CTRL1_XL 0x10
#define IMU_CTRL2_G  0x11
#define IMU_CTRL3_C  0x12
#define IMU_OUTX_L_G 0x22  // gyro X/Y/Z, then accel X/Y/Z

bool imuWrite(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(reg);
  Wire.write(value);
  return Wire.endTransmission() == 0;
}

bool imuRead(uint8_t reg, uint8_t *data, size_t len) {
  Wire.beginTransmission(IMU_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0 || Wire.requestFrom(IMU_ADDR, len) != len) {
    return false;
  }
  for (size_t i = 0; i < len; i++) {
    data[i] = Wire.read();
  }
  return true;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);  // the NX40's USB serial port opens with the monitor
  Wire.begin();

  uint8_t id;
  bool found = imuRead(IMU_WHO_AM_I, &id, 1) && id == 0x6A
               && imuWrite(IMU_CTRL3_C, 0x44)   // block data update, address auto-increment
               && imuWrite(IMU_CTRL1_XL, 0x40)  // accelerometer 104 Hz, +-2 g
               && imuWrite(IMU_CTRL2_G, 0x40);  // gyroscope 104 Hz, +-245 dps
  Serial.println(found ? "IMU found" : "IMU not found");
}

void loop() {
  uint8_t raw[12];
  if (imuRead(IMU_OUTX_L_G, raw, sizeof(raw))) {
    int16_t v[6];
    for (int i = 0; i < 6; i++) {
      v[i] = raw[2 * i] | raw[2 * i + 1] << 8;
    }
    Serial.print("accel g");
    for (int i = 3; i < 6; i++) {
      Serial.print(' ');
      Serial.print(v[i] * 0.000061f, 3);  // 0.061 mg/LSB at +-2 g
    }
    Serial.print("  gyro dps");
    for (int i = 0; i < 3; i++) {
      Serial.print(' ');
      Serial.print(v[i] * 0.00875f, 2);  // 8.75 mdps/LSB at +-245 dps
    }
    Serial.println();
  } else {
    Serial.println("IMU read failed");
  }
  delay(200);
}
