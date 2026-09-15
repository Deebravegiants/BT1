# [M] ImageMagick: Heap Buffer Over-Read in XCF decoder due to integer conversion overflow

## Summary
Severity: Medium
Advisory: GHSA-pjxj-pchx-4c3m
CVE: CVE-2026-53466
CWE: CWE-190, CWE-681
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-pjxj-pchx-4c3m
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
An integer overflow in the XCF decoder can result in an out of bounds read when a crafted image is read and that can result in a crash.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-pjxj-pchx-4c3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-53466
- https://github.com/ImageMagick/ImageMagick/commit/47ca7210515f3c9ea033b86fe4323a70caa74468
- https://github.com/ImageMagick/ImageMagick
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-26
- https://github.com/dlemstra/Magick.NET/releases/tag/14.15.0
