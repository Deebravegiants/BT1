# [M] ImageMagick has a heap buffer over-read via 32-bit integer overflow in MAT decoder

## Summary
Severity: Medium
Advisory: GHSA-mrmj-x24c-wwcv
CVE: CVE-2026-28692
CWE: CWE-125
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-mrmj-x24c-wwcv
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.4
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.4

## Details
In MAT decoder uses 32-bit arithmetic due to incorrect parenthesization resulting in a heap over-read.

```
=================================================================
==969652==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x506000003b40 at pc 0x555557b2a926 bp 0x7fffffff4c80 sp 0x7fffffff4c70
READ of size 8 at 0x506000003b40 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-mrmj-x24c-wwcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-28692
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.4
