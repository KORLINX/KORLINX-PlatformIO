# Copyright 2026 KORLINX
# Copyright 2026 Advanced Additive Manufacturing Systems Laboratory,
#   Sungkyunkwan University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Arduino framework on the KORLINX Arduino Zephyr core. The flags are the
# core's platform.txt recipes; the layout of this script follows
# builder/frameworks/arduino-zephyr.py of lee-lab-skku/platform-arduinoq.
# builder/zephyr.py does the link.

from os.path import isfile, join

from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()

FRAMEWORK_DIR = platform.get_package_dir("framework-arduino-korlinx-zephyr")
variant = board.get("build.variant")
variant_dir = join(FRAMEWORK_DIR, "variants", variant)
ldscripts = join(FRAMEWORK_DIR, "variants", "_ldscripts")

assert isfile(join(variant_dir, "includes.txt")), (
    "%s has no precompiled files for %s" % (FRAMEWORK_DIR, variant))

machine = "@%s" % join(variant_dir, "machine_flags.txt")
# compiler.zephyr.common_cxxflags and the code-generation part of
# compiler.zephyr.common_ldflags, which platform.txt also compiles C++ with
cxx_runtime = ["-fno-exceptions", "-fno-rtti", "-fno-unwind-tables",
               "-fno-threadsafe-statics", "-fno-use-cxa-atexit"]

env.Append(
    ASFLAGS=[machine],
    ASPPFLAGS=["-x", "assembler-with-cpp", machine],
    CFLAGS=["@%s" % join(variant_dir, "cflags.txt")],
    CXXFLAGS=["-std=gnu++17", "@%s" % join(variant_dir, "cxxflags.txt")]
    + cxx_runtime + ["-fno-extern-tls-init"],
    CCFLAGS=[
        "-g", "-Os", "-w", machine,
        "-imacros%s" % join(variant_dir, "llext-edk", "include", "zephyr",
                            "include", "generated", "zephyr", "autoconf.h"),
        "-imacros%s" % join(variant_dir, "llext-edk", "include", "zephyr",
                            "include", "zephyr", "toolchain", "zephyr_stdint.h"),
        "-fdata-sections", "-ffunction-sections",
        "-iprefix%s" % variant_dir,
        "@%s" % join(variant_dir, "includes.txt"),
    ],
    CPPDEFINES=[
        ("_PICOLIBC_CTYPE_SMALL", 1),
        ("ARDUINO", 10607),
        "ARDUINO_%s" % board.get("build.board"),
        "ARDUINO_ARCH_ZEPHYR",
        ("ARDUINO_LIBRARY_DISCOVERY_PHASE", 0),
    ],
    CPPPATH=[
        join(FRAMEWORK_DIR, "cores", "arduino"),
        join(FRAMEWORK_DIR, "cores", "arduino", "api", "deprecated"),
        join(FRAMEWORK_DIR, "cores", "arduino", "api", "deprecated-avr-comp"),
        variant_dir,
    ],
    LIBPATH=[variant_dir],
    LIBSOURCE_DIRS=[join(FRAMEWORK_DIR, "libraries")],
    LIBS=["stdc++", "supc++", "m", "gcc", "c"],
    LINKFLAGS=["-Wl,--gc-sections", "-Wl,-z,noexecstack", machine, "-std=gnu++17"]
    + cxx_runtime + ["-lnosys", "-nostdlib", "-Wl,-u,__cxa_allocate_exception",
                     "-e", "main", "-r"],
    # build.link_args.check-dynamic
    ZEPHYR_CHECK_LINKFLAGS=[
        "-T", join(variant_dir, "syms-dynamic.ld"),
        "-T", join(ldscripts, "memory-check.ld"),
        "-T", join(ldscripts, "build-static.ld")],
)
env.Replace(LDSCRIPT_PATH=join(ldscripts, "build-dynamic.ld"))

env.BuildSources(join("$BUILD_DIR", "FrameworkArduinoVariant"), variant_dir)
env.Prepend(LIBS=[env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"), join(FRAMEWORK_DIR, "cores", "arduino"))])
