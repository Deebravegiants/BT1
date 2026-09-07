# [H] ImageMagick: Policy Bypass can Trigger an Out-of-Memory condition

## Summary
Severity: High
Advisory: GHSA-q62c-h75r-2xhc
CVE: CVE-2026-53460
CWE: CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-q62c-h75r-2xhc
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.14.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.14.0

## Details
A missing check for maximum memory request in AcquireAlignedMemory could trigger an out-of-Memory condition.

## Credit
Aisle Research (Ze Sheng, Dmitrijs Trizna, Luigino Camastra, Guido Vranken)

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-q62c-h75r-2xhc
- https://nvd.nist.gov/vuln/detail/CVE-2026-53460
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.14.0
