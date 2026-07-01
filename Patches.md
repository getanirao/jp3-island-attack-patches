# Patch Documentation

ROM: `Jurassic Park III - Island Attack (USA).gba`
All offsets are ROM file offsets (= Ghidra address, no base offset needed
for this loader).

---

## Output header fixups

The distributed BPS patch and `Patch.py` output include the same two
header-byte updates produced by `gbafix` for the patched ROM:

| Offset | Original | Patched |
|---|---|---|
| `0x000000B4` | `00` | `80` |
| `0x000000BD` | `4A` | `CA` |

These do not affect gameplay logic, but they keep the patched output valid
for real hardware / flash cart use. Expected patched ROM CRC32:
`64E60724`.

---

## Patch 1 — Disable R-shoulder inventory cycling

**Effect:** R shoulder no longer cycles inventory. L still cycles forward
as normal. R is fully free for sprint use.

| Offset | Original | Patched |
|---|---|---|
| `0x0000FCD8` | `80` | `00` |

This zeroes the immediate value used to build the R-button bitmask
(`0x100`) inside the inventory-cycling function `FUN_0000fcb0`. With the
mask reduced to `0`, the `AND` check always evaluates to zero and the
cycling branch is never taken for R.

Verify: IWRAM `0x030042FA` (inventory slot index) should only change in
response to L presses.

---

## Patch 2 — Sprint: double-tap → hold R + direction

**Effect:** Holding R + any direction triggers sprint immediately.
Releasing either R or the direction stops sprint. Releasing R while still
holding a direction transitions cleanly to normal walking. Works in both
ISO and 2D stages (all three callers of the patched function were verified
to use the same parameter layout).

**Offsets:** `0x00001C2C` – `0x00001C51` (38 bytes, in-place replacement
of the original double-tap state machine, function `FUN_00001c2c`)

```
Offset  Bytes      Instruction              Meaning
1C2C    0A 1C      add  r2,r1,#0            r2 = sprint-state struct ptr
1C2E    03 88      ldrh r3,[r0,#0]          r3 = current held buttons
1C30    80 21      mov  r1,#0x80
1C32    49 00      lsl  r1,r1,#0x1          r1 = 0x100 (R button mask)
1C34    19 40      and  r1,r3               r1 = buttons & 0x100
1C36    07 D0      beq  ELSE                R not held -> ELSE
1C38    F0 21      mov  r1,#0xF0            direction mask (bits 4-7)
1C3A    19 40      and  r1,r3               r1 = buttons & 0xF0
1C3C    04 D0      beq  ELSE                no direction -> ELSE
1C3E    02 21      mov  r1,#2               -- SPRINT ACTIVE --
1C40    51 80      strh r1,[r2,#2]          state = 2 (sprinting)
1C42    D3 80      strh r3,[r2,#6]          output = full button word
1C44    18 1C      add  r0,r3,#0            return value
1C46    03 E0      b    EPILOGUE
1C48    00 21      mov  r1,#0               -- ELSE: no sprint --
1C4A    51 80      strh r1,[r2,#2]          state = 0
1C4C    D1 80      strh r1,[r2,#6]          output = 0
1C4E    00 20      mov  r0,#0               return 0
1C50    70 47      bx   lr                  -- EPILOGUE --
```

Raw byte sequence (38 bytes) for scripted patching:
```
0A 1C 03 88 80 21 49 00 19 40 07 D0 F0 21 19 40
04 D0 02 21 51 80 D3 80 18 1C 03 E0 00 21 51 80
D1 80 00 20 70 47
```

### Callers verified safe (all 3 use the same `param_1`/`param_2` layout)
- `0x0000B336` — main ISO/2D player update (`FUN_0000b354` family)
- `0x00028F68` — secondary player update, used in 2D mode (`FUN_00028f50`)
- `0x0002C28C` — menu/HUD context (`FUN_0002c268`); performs its own
  independent L/R inventory check immediately after the call, which reads
  the *separate* newly-pressed button struct and is unaffected by this
  patch

### Edge cases tested
- ✅ Hold R + direction → sprint engages
- ✅ Release direction, R still held → sprint stops, idle
- ✅ Release R, direction still held → sprint stops, walks normally
- ✅ Direction with no R → normal walk, no sprint
- ✅ R alone, no direction → no effect

---

## Planned

### Item crate hold-to-open
Goal: change the tap-repeatedly-on-crate interaction to hold-B.

**Findings:** The crate-hit-flag-consuming code (`entity+0xc0` bit 1,
gated by a check of `*0x03006BA8 & 2`) was traced to a function
(`FUN_0000b3be`, alongside a near-identical twin `FUN_0000b6a2`) that
fires on **every single frame regardless of player position** — confirmed
via Lua read-tracing while standing still far from any crate. This is
generic, shared per-entity HP/invincibility-frame handling code used by
many entity types (player, dinosaurs, breakable objects alike), not a
dedicated crate/box interaction.

Two attempted patches (flipping the `beq`/`bne` polarity at `0xB4A2`, and
NOPing the flag-clear at `0xB4F2`) produced no observed change in
behavior, and were reverted. Editing this function further risks
destabilizing the shared damage system across the entire game.

**Useful side-finding for future damage/HP work:**
- `entity+0x110` — appears to be HP/health-like field (decremented on hit)
- `entity+300` (0x12C) — appears to be an invincibility-frame countdown
- `entity+0xc0` bit 1 — "was hit this frame" flag, cleared after damage
  is applied

A future attempt should start from the crate's *spawn/init* code (to find
its unique entity-type ID) rather than the shared damage-application path,
since the generic code is reused too broadly to safely modify in place.

## Investigated, deferred

### Tutorial text edit
"Press the +Control Pad twice in one direction to dash!" is now
inaccurate after Patch 2. Text search for ASCII bytes returned no matches;
the game appears to use a custom font/tile encoding rather than standard
ASCII. Not yet located. Low priority (cosmetic).

## Key reference addresses

### IWRAM
| Address | Contents |
|---|---|
| `0x03003D00` | Remapped current button state (ushort) |
| `0x03003D02` | Remapped newly-pressed this frame (ushort) |
| `0x03003D08` | Button remap shift table [L,R,A,B], default `{9,8,0,1}` |
| `0x03003D10` | Raw (pre-remap) current button state (ushort) |
| `0x030042FA` | Inventory slot index (byte, 0–5) |
| `0x03006DFC` | Player entity base pointer |
| `0x03006BA8` | Shared "button held" flag word read by combat code |

### GBA button bitmasks (`REG_KEYINPUT`, active-LOW)
```
A=0x001  B=0x002  Select=0x004  Start=0x008
Right=0x010  Left=0x020  Up=0x040  Down=0x080
R=0x100  L=0x200
```

### Key ROM functions
| Function | Role |
|---|---|
| `FUN_00000b84` | Master game loop / input handler |
| `FUN_000009c0` | Per-frame update dispatcher (all 3 game modes) |
| `FUN_00036744` | Button remap validation + copy to IWRAM (runs at boot) |
| `FUN_00001c2c` | Sprint/dash state machine — **patched** |
| `FUN_0000fcb0` | Inventory cycling + HUD update — **patched** (R branch) |
| `FUN_0000b3be` / `FUN_0000b6a2` | Shared entity HP/damage/i-frame logic |
| `FUN_000109c4` | State-machine dispatcher (does not return) |

---

## Methodology notes for future contributors

- Many regions of this ROM (notably ~`0x21xxxx`, `0x31xxxx`, `0x40xxxx`,
  `0x66xxxx`) decompile to garbage in Ghidra's default analysis. The
  reliable fix is selecting the undefined byte range, **Disassemble →
  Disassemble - Thumb**, then **Create Function** at the correct start
  address (look for a `push {..., lr}` prologue).
- Many entity-update functions are reached only through runtime
  function-pointer jump tables, which Ghidra cannot resolve statically
  (shows as "Could not recover jumptable... too many branches"). For
  these, dynamic tracing in BizHawk Lua is the only practical approach:

  ```lua
  -- Find what reads/writes a RAM address, and from where
  event.on_bus_write(function(addr, val, flags)
      console.log(string.format("PC=%08X VAL=%d", emu.getregister("R15"), val))
  end, 0x03XXXXXX)
  while true do emu.frameadvance() end
  ```

  Use `event.on_bus_read` the same way; use `emu.getregister("R14")` to
  get the caller's return address (LR) when the producing PC is itself a
  generic shared subroutine.

- **Critical:** verify any candidate address actually correlates with the
  intended player action (not just general per-frame noise) before
  patching. Several apparent leads this session (`0x03006DE0`,
  `0x03006DF8`, multiple RAM Search hits) turned out to fire every frame
  regardless of input and were false positives. Standing completely
  still and confirming silence is the fastest sanity check.

- In-memory ROM patching in BizHawk Lua
  (`memory.usememorydomain("ROM"); memory.writebyte(...)`) is the fastest
  way to test a patch live before committing it to the ROM file via a hex
  editor — changes don't persist past a reboot, making iteration safe.
