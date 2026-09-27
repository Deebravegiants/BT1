# [M] ImageMagick has heap buffer overflow in WriteXWDImage due to CARD32 arithmetic overflow in bytes_per_line calculation

## Summary
Severity: Medium
Advisory: GHSA-qpg4-j99f-8xcg
CVE: CVE-2026-30937
CWE: CWE-122
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-qpg4-j99f-8xcg
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
A 32-bit unsigned integer overflow in the XWD (X Windows) encoder can cause an undersized heap buffer allocation. When writing a extremely large image an out of bounds heap write can occur.

```
=================================================================
==741961==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x5020000083dc at pc 0x56553b4c4245 bp 0x7ffd9d20fef0 sp 0x7ffd9d20fee0
WRITE of size 1 at 0x5020000083dc thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-qpg4-j99f-8xcg
- https://nvd.nist.gov/vuln/detail/CVE-2026-30937
- https://github.com/ImageMagick/ImageMagick
