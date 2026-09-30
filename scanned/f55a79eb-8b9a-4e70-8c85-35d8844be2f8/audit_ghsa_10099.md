# [M]  ImageMagick has a Stack Overflow via Recursive FX Expression Parsing

## Summary
Severity: Medium
Advisory: GHSA-f4qm-vj5j-9xpw
CVE: CVE-2026-33902
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-f4qm-vj5j-9xpw
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
A stack overflow vulnerability in ImageMagick's FX expression parser allows an attacker to crash the process by providing a deeply nested expression.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-f4qm-vj5j-9xpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33902
- https://github.com/ImageMagick/ImageMagick/commit/d3c0a37485314c5ccef72efb18f3847cd53868ba
- https://github.com/ImageMagick/ImageMagick
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
