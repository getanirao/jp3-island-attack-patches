# Jurassic Park III: Island Attack (GBA) — Control & QoL Patches

A community ROM patch for *Jurassic Park III: Island Attack* (Konami, 2001, GBA)
that fixes the game's most commonly criticized control issue: the unreliable
double-tap-to-dash mechanic.

No documented disassembly or ROM hack previously existed for this game. All
offsets below were found via manual reverse engineering with Ghidra, BizHawk,
and mGBA.

## What's fixed

### 1. Sprint: double-tap → hold R + direction
The original game required quickly double-tapping a directional input to
dash. Reviewers consistently called this out as a major control flaw:

> "This becomes a difficulty when trying to press diagonally twice in order
> to run from Spinosaurus... The GBA control pad can be very sensitive when
> trying to tap, and it's nearly impossible for gamers with large hands."

This patch replaces the double-tap detection with a simple, responsive
**hold R + direction to sprint** scheme, working in both isometric (freeroam)
and 2D (cross-section) stages.

### 2. Inventory cycling: L only
The R shoulder button no longer cycles inventory items, freeing it
exclusively for sprint. L still cycles inventory normally.

## Applying the patch

1. Obtain a legally-dumped copy of `Jurassic Park III - Island Attack (USA).gba`
   (this repo does not include or link to ROM files)
2. Apply the patch using one of the following methods:
   - **BPS patch (recommended):** Open [`jp3-qol-patches.bps`](jp3-qol-patches.bps)
     in [FLIPS](https://github.com/Alcaro/Flips), select your ROM, and save the
     patched copy.
   - **Python script:** Run the included [`Patch.py`](Patch.py) script:
     ```
     python Patch.py "Jurassic Park III - Island Attack (USA).gba" patched.gba
     ```
   - **Manual hex edit:** Apply the byte changes listed in
     [`Patches.md`](Patches.md) using a hex editor.
3. Run [`gbafix`](https://github.com/devkitPro/gba-tools) on the output to
   fix the ROM header checksum (required for real hardware / EverDrive use).

Expected clean ROM CRC32: `1E7048D2`. The Python script verifies the ROM size
and CRC32 before writing changes.

## Status

| Patch | Status |
|---|---|
| Sprint (hold R + direction) |  Complete, tested |
| Inventory cycling (L only) |  Complete, tested |
| Item crate hold-to-open |  Investigated, deferred (see notes) |
| Stun gun / damage balance |  Planned |

See [`Patches.md`](Patches.md) for full technical documentation, byte-level
patch details, and notes on what's been investigated for future work.

## Tools used

- [Ghidra](https://ghidra-sre.org/) with the
  [pudii/gba-ghidra-loader](https://github.com/pudii/gba-ghidra-loader)
  extension
- [BizHawk](https://tasvideos.org/BizHawk) (RAM Search, Lua scripting)
- [mGBA](https://mgba.io/) (debugger)
- [HexEd.it](https://hexed.it) (browser-based hex editor)

## Disclaimer

This repository contains no copyrighted ROM data — only documented byte
offsets and replacement values for a ROM you must legally own and dump
yourself. Jurassic Park III: Island Attack is © Konami / Universal /
Amblin Entertainment. This is an unofficial, non-commercial fan patch.
