# [M] ImageMagick has Heap Buffer Over-Read in BilateralBlurImage

## Summary
Severity: Medium
Advisory: GHSA-cqw9-w2m7-r2m2
CVE: CVE-2026-30935
CWE: CWE-125
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-cqw9-w2m7-r2m2
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
BilateralBlurImage contains a heap buffer over-read caused by an incorrect conversion. When processing a crafted image with the `-bilateral-blur` operation an out of bounds read can occur.

```
=================================================================
==676172==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x50a0000079c0 at pc 0x57b483c722f7 bp 0x7fffc0acd380 sp 0x7fffc0acd370
READ of size 4 at 0x50a0000079c0 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-cqw9-w2m7-r2m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-30935
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.4
