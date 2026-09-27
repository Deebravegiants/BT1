# [M] ImageMagick Has Signed Integer Overflow in SIXEL Decoder, Leading to Memory Corruption

## Summary
Severity: Medium
Advisory: GHSA-xg29-8ghv-v4xr
CVE: CVE-2026-25970
CWE: CWE-190
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-xg29-8ghv-v4xr
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
A signed integer overflow vulnerability in ImageMagick's SIXEL decoder allows an attacker to trigger memory corruption and denial of service when processing a maliciously crafted SIXEL image file. The vulnerability occurs during buffer reallocation operations where pointer arithmetic using signed 32-bit integers overflows.

```
AddressSanitizer:DEADLYSIGNAL
=================================================================
==143838==ERROR: AddressSanitizer: UNKNOWN SIGNAL on unknown address 0x000000000000
    #0 0x7f379d5adb53  (/lib/x86_64-linux-gnu/libc.so.6+0xc4b53)
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-xg29-8ghv-v4xr
- https://nvd.nist.gov/vuln/detail/CVE-2026-25970
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3
