# [H] ImageMagick is vulnerable to an integer Overflow in TIM decoder leading to out of bounds read (32-bit only)

## Summary
Severity: High
Advisory: GHSA-6hjr-v6g4-3fm8
CVE: CVE-2025-66628
CWE: CWE-125
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-6hjr-v6g4-3fm8
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.0

## Details
### Summary
The TIM (PSX TIM) image parser in ImageMagick contains a critical integer overflow vulnerability in the `ReadTIMImage` function (`coders/tim.c`). The code reads `width` and `height` (16-bit values) from the file header and calculates `image_size = 2 * width * height` without checking for overflow.
On 32-bit systems (or where `size_t` is 32-bit), this calculation can overflow if `width` and `height` are large (e.g., 65535), wrapping around to a small value. This results in a small heap allocation via `AcquireQuantumMemory` and later operations relying on the dimensions can trigger an out of bounds read.
### Vulnerable Code
File: `coders/tim.c`
```c
width=ReadBlobLSBShort(image);
height=ReadBlobLSBShort(image);
image_size=2*width*height;       // Line 234 - NO OVERFLOW CHECK!
```

### Impact
This vulnerability can lead to Arbitrary Memory Disclosure due to an out of bounds read on 32-bit systems.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-6hjr-v6g4-3fm8
- https://github.com/dlemstra/Magick.NET/commit/2dfa08e15cfd11016a79615994787b14f9048b1c
- https://github.com/ImageMagick/ImageMagick
