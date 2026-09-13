# [M] ImageMagick: Heap Buffer Over-Write in morphology operation when an invalid kernel is provided

## Summary
Severity: Medium
Advisory: GHSA-f5m7-cqgw-8hm7
CVE: CVE-2026-62343
CWE: CWE-190
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-f5m7-cqgw-8hm7
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.15.0

## Details
An invalid kernel can cause a heap buffer over-write when performing a morphology operation with a user supplied kernel.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-f5m7-cqgw-8hm7
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.15.0
