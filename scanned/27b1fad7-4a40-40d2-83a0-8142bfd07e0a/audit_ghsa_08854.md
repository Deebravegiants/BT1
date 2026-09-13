# [M] ImageMagick: Heap Buffer Over-Write in distributed pixel cache server

## Summary
Severity: Medium
Advisory: GHSA-p93h-f2jc-477j
CVE: CVE-2026-46692
CWE: CWE-122
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-p93h-f2jc-477j
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.12.0

## Details
An attacker who can connect to a `magick -distribute-cache` service can cause a heap buffer over-write in the server process.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-p93h-f2jc-477j
- https://github.com/ImageMagick/ImageMagick
