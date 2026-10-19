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
# Build and upload for boards on the KORLINX Arduino Zephyr core
# (build.core = zephyr). The sketch is linked as a Zephyr LLEXT and runs
# inside the precompiled loader firmware that ships with the core. The link
# follows the core's platform.txt; the multi-pass link is adapted from
# builder/artifacts/zephyr-llext.py of lee-lab-skku/platform-arduinoq.

from os.path import join
from platform import system

from SCons.Script import AlwaysBuild, Builder, COMMAND_LINE_TARGETS, Default, Import

Import("env")

platform = env.PioPlatform()
board = env.BoardConfig()


def tool(package, name):
    return join(platform.get_package_dir(package) or "", name)


env.Replace(
    AR="arm-zephyr-eabi-gcc-ar",
    AS="arm-zephyr-eabi-as",
    CC="arm-zephyr-eabi-gcc",
    CXX="arm-zephyr-eabi-g++",
    GDB="arm-zephyr-eabi-gdb",
    OBJCOPY="arm-zephyr-eabi-objcopy",
    RANLIB="arm-zephyr-eabi-gcc-ranlib",
    STRIP="arm-zephyr-eabi-strip",
    ARFLAGS=["rc"],
    PROGSUFFIX=".elf",
    ZEPHYRSKETCH=tool("tool-zephyr-sketch-tool", "zephyr-sketch-tool"),
    GENRODATALD=tool("tool-gen-rodata-ld", "gen-rodata-ld"),
    ZEPHYRCHECKSIZE=tool("tool-zephyr-check-size", "zephyr-check-size"),
    # the precompiled loader firmware the sketch runs in
    ZEPHYR_LOADER_HEX=tool("framework-arduino-korlinx-zephyr", join(
        "firmwares", "zephyr-%s.hex" % board.get("build.variant"))),
    ZEPHYR_LOADER_CONFIG=tool("framework-arduino-korlinx-zephyr", join(
        "firmwares", "zephyr-%s.config" % board.get("build.variant"))),
)
if env.subst("$PROGNAME") in ("", "program"):
    env.Replace(PROGNAME="firmware")

# platform.txt: build.zsk_args.debug (Debug menu) and startup mode "wait"
env.Replace(ZEPHYRSKETCHFLAGS="-debug" if board.get("build.zsk_debug", "") else "")

env.Append(
    BUILDERS=dict(
        StripElf=Builder(
            action=env.VerboseAction(
                '"$STRIP" --strip-debug "$SOURCE" -o "$TARGET"', "Stripping $TARGET"),
            suffix=".elf"),
        GenRodataLd=Builder(
            action=env.VerboseAction(
                '"$GENRODATALD" "$SOURCE" "$TARGET" dynamic',
                "Generating $TARGET")),
        PackSketch=Builder(
            action=env.VerboseAction(
                '"$ZEPHYRSKETCH" $ZEPHYRSKETCHFLAGS -output "$TARGET" "$SOURCE"',
                "Packing $TARGET")),
    )
)

sketch_bin = join("$BUILD_DIR", "${PROGNAME}.elf-zsk.bin")

if "nobuild" not in COMMAND_LINE_TARGETS:
    env.ProcessProgramDeps()
    env.ProcessProjectDeps()
    # the core archive and the libraries reference each other
    env.Prepend(_LIBFLAGS="-Wl,--start-group ")
    env.Append(_LIBFLAGS=" -Wl,--end-group")

    sources = env.get("PIOBUILDFILES", [])
    dynamic_ld = env["LDSCRIPT_PATH"]
    env.Replace(LDSCRIPT_PATH="")

    # recipe.c.combine.1: link as a static program once, so a sketch that
    # cannot resolve or fit fails here instead of when the loader runs it
    check = env.Clone()
    check.Replace(LINKFLAGS=[f for f in env["LINKFLAGS"] if f != "-r"])
    check.Append(LINKFLAGS=env["ZEPHYR_CHECK_LINKFLAGS"])
    check_elf = check.Program(join("$BUILD_DIR", "${PROGNAME}_check"), sources)

    # recipe.c.combine.2-4: relocatable link, split .rodata, link again
    temp = env.Clone()
    temp.Append(LINKFLAGS=["-T", dynamic_ld])
    temp_elf = temp.Program(join("$BUILD_DIR", "${PROGNAME}_temp"), sources)
    env.Depends(temp_elf, check_elf)
    rodata_ld = env.GenRodataLd(join("$BUILD_DIR", "rodata_split.ld"), temp_elf)

    final = env.Clone()
    final.Append(LINKFLAGS=[
        "-T", rodata_ld[0], "-T", dynamic_ld,
        "-Wl,-Map,%s" % join("$BUILD_DIR", "${PROGNAME}.map")])
    debug_elf = final.Program(join("$BUILD_DIR", "${PROGNAME}_debug"), sources)
    env.Depends(debug_elf, rodata_ld)
    env.Replace(PIOMAINPROG=debug_elf, PROGPATH=debug_elf[0])

    sketch_elf = env.StripElf(join("$BUILD_DIR", "${PROGNAME}"), debug_elf)
    sketch_bin = env.PackSketch(sketch_bin, sketch_elf)

    # recipe.size.pattern; read by PlatformIO's own size check
    env.Replace(
        SIZECHECKCMD=["$ZEPHYRCHECKSIZE", "dynamic", "$ZEPHYR_LOADER_CONFIG",
                      env.subst(sketch_bin[0].get_abspath()),
                      env.subst(sketch_elf[0].get_abspath())],
        SIZEPROGREGEXP=r"^\.text\s+(\d+)",
        SIZEDATAREGEXP=r"^\.data\s+(\d+)",
    )
    size = AlwaysBuild(env.Alias(
        "checkprogsize", sketch_bin,
        env.VerboseAction(env.CheckUploadSize, "Checking size $SOURCE")))
    env.Depends("upload", size)
    Default([sketch_bin, size])
else:
    Default([sketch_bin])

AlwaysBuild(env.Alias("nobuild", sketch_bin))
env.Alias("buildprog", sketch_bin)


# Upload: the loader once, the sketch at upload.offset_address. J-Link skips
# flash that already matches, so an unchanged loader is not rewritten.
def jlink_script(env, source):
    path = join(env.subst("$BUILD_DIR"), "upload.jlink")
    with open(path, "w") as fp:
        fp.write("\n".join([
            "r",
            'loadfile "%s"' % env.subst("$ZEPHYR_LOADER_HEX"),
            'loadfile "%s" %s' % (source, board.get("upload.offset_address")),
            "r", "g", "q", ""]))
    return path


env.Replace(
    __jlink_script=jlink_script,
    UPLOADER="JLink.exe" if system() == "Windows" else "JLinkExe",
    UPLOADERFLAGS=[
        "-device", board.get("debug.jlink_device"),
        "-speed", env.GetProjectOption("debug_speed", "4000"),
        "-if", "swd",
        "-autoconnect", "1",
        "-NoGui", "1",
    ] + (["-USB", "$UPLOAD_PORT"] if env.subst("$UPLOAD_PORT") else []),
    UPLOADCMD='$UPLOADER $UPLOADERFLAGS -CommanderScript "${__jlink_script(__env__, SOURCE)}"',
)
AlwaysBuild(env.Alias(
    "upload", sketch_bin, env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")))
