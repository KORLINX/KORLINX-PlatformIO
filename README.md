# KORLINX: development platform for PlatformIO

PlatformIO support for KORLINX nRF52 boards. It builds with the same
[KORLINX nRF52 Arduino core](https://github.com/KORLINX/KORLINX-nRF52-Arduino)
the Arduino IDE installs as `korlinx:nrf52`, from the same release archive.

| Board | `board =` | MCU | Arduino FQBN |
|---|---|---|---|
| [NX40 nRF52840](https://wiki.korlinx.com/docs/Network/Bluetooth/NX40_Dev_Kit/NX40_Dev_Kit_Overview) | `nx40` | nRF52840, S140 6.1.1 | `korlinx:nrf52:nx40` |

## Use it

```ini
[env:nx40]
platform = https://github.com/KORLINX/KORLINX-PlatformIO.git#1.0.0
board = nx40
framework = arduino
```

Pin a release tag as above so a project keeps building the same way. Without
`#<tag>` PlatformIO takes `main` once and keeps that copy until you run
`pio pkg update`.

Upload goes over USB through the UF2/DFU bootloader. PlatformIO finds the
board, resets it into the bootloader and flashes it; no button press needed.

```sh
pio run -t upload
pio device monitor
```

A sketch that uses `Serial` must `#include <Adafruit_TinyUSB.h>`, the same as
in the Arduino IDE. The examples show this.

### Debug and log options

The Arduino IDE menus map to build flags:

| Arduino IDE menu | `build_flags` |
|---|---|
| Debug: Level 1 (Error Message) | `-DCFG_DEBUG=1` |
| Debug: Level 2 (Full Debug) | `-DCFG_DEBUG=2` |
| Debug: Level 3 (Segger SystemView) | `-DCFG_DEBUG=3 -DCFG_SYSVIEW=1` |
| Debug output: Serial1 | `-DCFG_LOGGER=1 -DCFG_TUSB_DEBUG=CFG_DEBUG` |
| Debug output: Segger RTT | `-DCFG_LOGGER=2 -DCFG_TUSB_DEBUG=CFG_DEBUG -DSEGGER_RTT_MODE_DEFAULT=SEGGER_RTT_MODE_BLOCK_IF_FIFO_FULL` |

The defaults are Level 0 and Serial, the same as the Arduino IDE.

### Other upload methods

The platform also carries PlatformIO's SWD upload paths, `upload_protocol =
jlink`, `nrfjprog` or `cmsis-dap`, and `pio run -t bootloader`, which writes
the KORLINX bootloader with `nrfjprog`. These come unchanged from
platform-nordicnrf52 and have not yet been tested on an NX40; USB upload has.

## Examples

`examples/` has Blink, USB Serial and the Bluefruit BLE UART peripheral. They
use the short name `platform = korlinx`, so install the platform once, then
build one:

```sh
pio pkg install -g -p https://github.com/KORLINX/KORLINX-PlatformIO.git#1.0.0
pio run -d examples/arduino-blink
```

## How releases flow

```
KORLINX-nRF52-Arduino: tag vX.Y.Z
  └─ Release workflow builds KXduino_nRF52-X.Y.Z.tar.bz2 once, publishes it,
     adds it to package_korlinx_index.json  ─────────►  Arduino IDE
     and dispatches Bump core here
KORLINX-PlatformIO: Bump core opens a PR that pins the new archive URL
  └─ Examples workflow builds it; merge, bump "version", tag  ─►  PlatformIO
```

Both installers get the same core files from the same archive: it carries
`package.json` for PlatformIO next to `platform.txt` for the Arduino IDE.

## Develop against a local core

```ini
platform = symlink:///path/to/KORLINX-PlatformIO
platform_packages =
    framework-arduino-korlinx-nrf52 @ symlink:///path/to/KORLINX-nRF52-Arduino
```

## Credits

The build scripts come from PlatformIO's
[platform-nordicnrf52](https://github.com/platformio/platform-nordicnrf52)
and [builder-framework-arduino-nrf5](https://github.com/platformio/builder-framework-arduino-nrf5),
Apache-2.0. Each adapted file says where it came from and what changed.
