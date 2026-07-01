#!/usr/bin/env python3
"""
Patch script for Jurassic Park III: Island Attack (USA) [GBA]

Applies the control/QoL patches documented in Patches.md:
  1. Disables R-shoulder inventory cycling (frees R for sprint)
  2. Replaces the double-tap-to-dash mechanic with hold-R-plus-direction

Usage:
    python Patch.py <input.gba> <output.gba>

After patching, run `gbafix` on the output file to fix the ROM header
checksum (required for real hardware / EverDrive use):
    gbafix output.gba
"""

import binascii
import sys

EXPECTED_SOURCE_SIZE = 0x800000
EXPECTED_SOURCE_CRC32 = 0x1E7048D2
EXPECTED_PATCHED_CRC32 = 0x4669F5BC

PATCHES = [
    {
        "name": "Inventory cycling (disable R)",
        "offset": 0xFCD8,
        "expected": bytes.fromhex("80"),
        "replacement": bytes.fromhex("00"),
    },
    {
        "name": "Sprint (hold R + direction)",
        "offset": 0x1C2C,
        "expected": None,
        "replacement": bytes.fromhex(
            "0A 1C 03 88 80 21 49 00 19 40 07 D0 F0 21 19 40 "
            "04 D0 02 21 51 80 D3 80 18 1C 03 E0 00 21 51 80 "
            "D1 80 00 20 70 47"
        ),
    },
]


def crc32(data: bytes) -> int:
    return binascii.crc32(data) & 0xFFFFFFFF


def format_crc(value: int) -> str:
    return f"0x{value:08X}"


def validate_source_rom(data: bytes) -> None:
    errors = []

    if len(data) != EXPECTED_SOURCE_SIZE:
        errors.append(
            f"input size is 0x{len(data):X} bytes; expected "
            f"0x{EXPECTED_SOURCE_SIZE:X} bytes"
        )

    actual_crc = crc32(data)
    if actual_crc == EXPECTED_PATCHED_CRC32:
        errors.append("input already appears to be patched")
    elif actual_crc != EXPECTED_SOURCE_CRC32:
        errors.append(
            f"input CRC32 is {format_crc(actual_crc)}; expected clean ROM "
            f"CRC32 {format_crc(EXPECTED_SOURCE_CRC32)}"
        )

    for patch in PATCHES:
        expected = patch["expected"]
        if expected is None:
            continue

        offset = patch["offset"]
        actual = data[offset:offset + len(expected)]
        if actual != expected:
            errors.append(
                f"{patch['name']} original byte check failed at "
                f"0x{offset:X}: expected {expected.hex(' ').upper()}, "
                f"found {actual.hex(' ').upper()}"
            )

    if errors:
        print("ERROR: refusing to patch this ROM:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


def apply_patches(data: bytearray) -> bytearray:
    for patch in PATCHES:
        name = patch["name"]
        offset = patch["offset"]
        replacement = patch["replacement"]
        print(f"Applying: {name}")
        data[offset:offset + len(replacement)] = replacement
        print(f"  {len(replacement)} byte(s) written.")
    return data


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.gba> <output.gba>")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path, "rb") as f:
        data = bytearray(f.read())

    validate_source_rom(data)

    data = apply_patches(data)
    patched_crc = crc32(data)
    if patched_crc != EXPECTED_PATCHED_CRC32:
        print(
            f"ERROR: patched output CRC32 is {format_crc(patched_crc)}; "
            f"expected {format_crc(EXPECTED_PATCHED_CRC32)}. Aborting."
        )
        sys.exit(1)

    with open(out_path, "wb") as f:
        f.write(data)

    print(f"\nDone. Wrote patched ROM to: {out_path}")
    print("Remember to run `gbafix` on the output before using on real hardware.")


if __name__ == "__main__":
    main()
