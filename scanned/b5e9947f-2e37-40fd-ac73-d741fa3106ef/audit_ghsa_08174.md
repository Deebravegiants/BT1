# [M] ImageMagick has a heap Buffer Over-read  in its DJVU image format handler

## Summary
Severity: Medium
Advisory: GHSA-r99p-5442-q2x2
CVE: CVE-2026-27799
CWE: CWE-122, CWE-126
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-r99p-5442-q2x2
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
A heap Buffer Over-read vulnerability exists in the DJVU image format handler. The vulnerability occurs due to integer truncation when calculating the stride (row size) for pixel buffer allocation. The stride calculation overflows a 32-bit signed integer, resulting in an out-of-bounds memory reads.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-r99p-5442-q2x2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27799
- https://github.com/ImageMagick/ImageMagick/commit/e87695b3227978ad70b967b8d054baaf8ac2cced
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.10.3
