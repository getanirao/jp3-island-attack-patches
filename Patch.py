#!/usr/bin/env python3
"""
Patch script for Jurassic Park III: Island Attack (USA) [GBA]

Applies the control/QoL patches documented in PATCHES.md:
  1. Disables R-shoulder inventory cycling (frees R for sprint)
  2. Replaces the double-tap-to-dash mechanic with hold-R-plus-direction

Usage:
    python patch.py <input.gba> <output.gba>

After patching, run `gbafix` on the output file to fix the ROM header
checksum (required for real hardware / EverDrive use):
    gbafix output.gba
"""

import sys

# (offset, original_byte_or_None, new_byte) -- original is checked if not None
PATCH_1_INVENTORY = [
    (0xFCD8, 0x80, 0x00),
]

PATCH_2_SPRINT = [
    (0x1C2C, None, 0x0A), (0x1C2D, None, 0x1C),
    (0x1C2E, None, 0x03), (0x1C2F, None, 0x88),
    (0x1C30, None, 0x80), (0x1C31, None, 0x21),
    (0x1C32, None, 0x49), (0x1C33, None, 0x00),
    (0x1C34, None, 0x19), (0x1C35, None, 0x40),
    (0x1C36, None, 0x07), (0x1C37, None, 0xD0),
    (0x1C38, None, 0xF0), (0x1C39, None, 0x21),
    (0x1C3A, None, 0x19), (0x1C3B, None, 0x40),
    (0x1C3C, None, 0x04), (0x1C3D, None, 0xD0),
    (0x1C3E, None, 0x02), (0x1C3F, None, 0x21),
    (0x1C40, None, 0x51), (0x1C41, None, 0x80),
    (0x1C42, None, 0xD3), (0x1C43, None, 0x80),
    (0x1C44, None, 0x18), (0x1C45, None, 0x1C),
    (0x1C46, None, 0x03), (0x1C47, None, 0xE0),
    (0x1C48, None, 0x00), (0x1C49, None, 0x21),
    (0x1C4A, None, 0x51), (0x1C4B, None, 0x80),
    (0x1C4C, None, 0xD1), (0x1C4D, None, 0x80),
    (0x1C4E, None, 0x00), (0x1C4F, None, 0x20),
    (0x1C50, None, 0x70), (0x1C51, None, 0x47),
]

ALL_PATCHES = {
    "Inventory cycling (disable R)": PATCH_1_INVENTORY,
    "Sprint (hold R + direction)": PATCH_2_SPRINT,
}


def apply_patches(data: bytearray) -> bytearray:
    for name, patch in ALL_PATCHES.items():
        print(f"Applying: {name}")
        for offset, expected, new_value in patch:
            if expected is not None and data[offset] != expected:
                print(
                    f"  WARNING: offset 0x{offset:X} expected 0x{expected:02X}, "
                    f"found 0x{data[offset]:02X}. Applying anyway, but verify "
                    f"this is the correct ROM version."
                )
            data[offset] = new_value
        print(f"  {len(patch)} byte(s) written.")
    return data


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.gba> <output.gba>")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path, "rb") as f:
        data = bytearray(f.read())

    if len(data) < 0x1C52:
        print("ERROR: input file is too small to be this ROM. Aborting.")
        sys.exit(1)

    data = apply_patches(data)

    with open(out_path, "wb") as f:
        f.write(data)

    print(f"\nDone. Wrote patched ROM to: {out_path}")
    print("Remember to run `gbafix` on the output before using on real hardware.")


if __name__ == "__main__":
    main()