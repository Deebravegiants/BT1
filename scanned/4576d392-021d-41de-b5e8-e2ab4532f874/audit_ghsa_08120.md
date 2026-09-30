# [M] ImageMagick has a heap buffer over-read in its MAP image decoder

## Summary
Severity: Medium
Advisory: GHSA-42p5-62qq-mmh7
CVE: CVE-2026-25987
CWE: CWE-125
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-42p5-62qq-mmh7
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-OpenMP-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
A heap buffer over-read vulnerability exists in the MAP image decoder when processing crafted MAP files, potentially leading to crashes or unintended memory disclosure during image decoding.

```
=================================================================
==4070926==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x502000002b31 at pc 0x56517afbd910 bp 0x7ffc59e90000 sp 0x7ffc59e8fff0
READ of size 1 at 0x502000002b31 thread T0
```

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-42p5-62qq-mmh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25987
- https://github.com/ImageMagick/ImageMagick/commit/bbae0215e1b76830509fd20e6d37c0dd7e3e4c3a
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3
