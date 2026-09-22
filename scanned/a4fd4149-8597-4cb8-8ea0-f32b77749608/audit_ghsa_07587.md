# [M] ImageMagick: Out of bounds read in multiple coders read raw pixel data

## Summary
Severity: Medium
Advisory: GHSA-jv4p-gjwq-9r2j
CVE: CVE-2026-25576
CWE: CWE-122
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-jv4p-gjwq-9r2j
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
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.10.3
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.10.3

## Details
A heap buffer over-read vulnerability exists in multiple raw image format handles. The vulnerability occurs when processing images with -extract dimensions larger than -size dimensions, causing out-of-bounds memory reads from a heap-allocated buffer.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-jv4p-gjwq-9r2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-25576
- https://github.com/ImageMagick/ImageMagick/commit/077b42643212d7da8c1a4f6b2cd0067ebca8ec0f
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3
