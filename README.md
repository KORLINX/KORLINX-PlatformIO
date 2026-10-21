# KORLINX: development platform for PlatformIO

PlatformIO support for KORLINX boards. Each board builds with the same
Arduino core, from the same release archive, that the Arduino IDE installs.

| Board | `board =` | MCU | Arduino core | Arduino FQBN |
|---|---|---|---|---|
| [NX40 nRF52840](https://wiki.korlinx.com/docs/Network/Bluetooth/NX40_Dev_Kit/NX40_Dev_Kit_Overview) | `nx40` | nRF52840, S140 6.1.1 | [KORLINX-nRF52-Arduino](https://github.com/KORLINX/KORLINX-nRF52-Arduino) | `korlinx:nrf52:nx40` |
| [NX15 nRF54L15](https://wiki.korlinx.com/docs/Network/Bluetooth/NX15_Dev_Kit/NX15_Dev_Kit_Overview) | `nx15` | nRF54L15 | [ArduinoCore-zephyr](https://github.com/KORLINX/ArduinoCore-zephyr) | `korlinx:zephyr:nx15` |

## Use it

```ini
[env:nx40]
platform = https://github.com/KORLINX/KORLINX-PlatformIO.git#1.1.0
board = nx40
framework = arduino
```

Use `board = nx15` for the NX15. Pin a release tag as above so a project keeps
building the same way. Without `#<tag>` PlatformIO takes `main` once and keeps
that copy until you run `pio pkg update`.

```sh
pio run -t upload
pio device monitor
```

### NX40

Upload goes over USB through the UF2/DFU bootloader. PlatformIO finds the
board, resets it into the bootloader and flashes it; no button press needed.

A sketch that uses `Serial` must `#include <Adafruit_TinyUSB.h>`, the same as
in the Arduino IDE. The examples show this.

The Arduino IDE debug menus map to build flags:

| Arduino IDE menu | `build_flags` |
|---|---|
| Debug: Level 1 (Error Message) | `-DCFG_DEBUG=1` |
| Debug: Level 2 (Full Debug) | `-DCFG_DEBUG=2` |
| Debug: Level 3 (Segger SystemView) | `-DCFG_DEBUG=3 -DCFG_SYSVIEW=1` |
| Debug output: Serial1 | `-DCFG_LOGGER=1 -DCFG_TUSB_DEBUG=CFG_DEBUG` |
| Debug output: Segger RTT | `-DCFG_LOGGER=2 -DCFG_TUSB_DEBUG=CFG_DEBUG -DSEGGER_RTT_MODE_DEFAULT=SEGGER_RTT_MODE_BLOCK_IF_FIFO_FULL` |

The defaults are Level 0 and Serial, the same as the Arduino IDE.

The platform also carries PlatformIO's SWD upload paths, `upload_protocol =
jlink`, `nrfjprog` or `cmsis-dap`, and `pio run -t bootloader`, which writes
the KORLINX bootloader with `nrfjprog`. These come unchanged from
platform-nordicnrf52 and have not yet been tested on an NX40; USB upload has.

### NX15

The sketch runs inside a loader firmware that ships with the core. Upload goes
through a J-Link: the first upload writes the loader and the sketch, later ones
only the sketch, since J-Link skips flash that already matches. With several
J-Links attached, pick one by its serial number:

```ini
upload_port = 12345678
```

`Serial` is the board's USB-UART, 115200 baud. Debugging with `pio debug` is
not supported yet.

## Examples

| Example | Board | Shows |
|---|---|---|
| `arduino-blink` | NX40, NX15 | The built-in LED |
| `arduino-usb-serial` | NX40 | `Serial` over USB |
| `arduino-ble-uart` | NX40 | The Bluefruit BLE UART peripheral |
| `arduino-leds` | NX40, NX15 | The four LEDs in turn |
| `arduino-button` | NX40, NX15 | The button, debounced |
| `arduino-fade` | NX40, NX15 | `analogWrite()` on the red LED |
| `arduino-analog` | NX40, NX15 | `analogRead()` on the J3 header |
| `arduino-serial-echo` | NX40, NX15 | Lines read from `Serial` and sent back |
| `arduino-shtc3` | NX40, NX15 | SHTC3 temperature and humidity on `Wire` |
| `arduino-imu` | NX40, NX15 | Acceleration and rotation from the IMU on `Wire` |

The examples use the short name `platform = korlinx`, so install the platform
once, then build one:

```sh
pio pkg install -g -p https://github.com/KORLINX/KORLINX-PlatformIO.git#1.1.0
pio run -d examples/arduino-blink
```

An example for both boards has an `nx40` and an `nx15` environment, and
`pio run` builds both. Pick one with `-e`:

```sh
pio run -d examples/arduino-leds -e nx15 -t upload
```

## How releases flow

```
KORLINX-nRF52-Arduino: tag vX.Y.Z
  └─ Release workflow builds KXduino_nRF52-X.Y.Z.tar.gz once, publishes it,
     adds it to package_korlinx_index.json  ─────────►  Arduino IDE
KORLINX-PlatformIO: run Bump core with X.Y.Z; it opens a PR that pins the
  new archive URL
  └─ Examples workflow builds it; merge, bump "version", tag  ─►  PlatformIO
```

The NX15 core, KORLINX/ArduinoCore-zephyr, publishes `korlinx-X.Y.Z.tar.gz`
next to the archive the Arduino IDE installs, and, when its toolchain or
tools change, those tools repacked for PlatformIO
(`extra/package_platformio_tools.py`). Point `platform.json` at the new
release by hand.

Both installers get the same core files from the same archive: it carries
`package.json` for PlatformIO next to `platform.txt` for the Arduino IDE.

## Develop against a local core

```ini
platform = symlink:///path/to/KORLINX-PlatformIO
platform_packages =
    framework-arduino-korlinx-nrf52 @ symlink:///path/to/KORLINX-nRF52-Arduino
```

For the NX15, override `framework-arduino-korlinx-zephyr` the same way with a
packaged core that has its precompiled `variants/` and `firmwares/`.

## Credits

The build scripts come from PlatformIO's
[platform-nordicnrf52](https://github.com/platformio/platform-nordicnrf52)
and [builder-framework-arduino-nrf5](https://github.com/platformio/builder-framework-arduino-nrf5),
and, for the NX15, from
[platform-arduinoq](https://github.com/lee-lab-skku/platform-arduinoq), all
Apache-2.0. Each adapted file says where it came from and what changed.
