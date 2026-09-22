# [M] ImageMagick has heap-based buffer overflow in UHDR encoder

## Summary
Severity: Medium
Advisory: GHSA-h95r-c8c7-mrwx
CVE: CVE-2026-30931
CWE: CWE-122
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-h95r-c8c7-mrwx
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.4

## Details
A heap-based buffer overflow in the UHDR encoder can happen due to truncation of a value and it would allow an out of bounds write.

```
================================================================
==2158399==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x521000039500 at pc 0x562a4a42f968 bp 0x7ffcca4ed6c0 sp 0x7ffcca4ed6b0
WRITE of size 1 at 0x521000039500 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-h95r-c8c7-mrwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-30931
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.4
