# [M] ImageMagick has a heap buffer overflow (WRITE) in the YAML and JSON encoders.

## Summary
Severity: Medium
Advisory: GHSA-5592-p365-24xh
CVE: CVE-2026-40169
CWE: CWE-122
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-5592-p365-24xh
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
A crafted image could result in an out of bounds heap write when writing a yaml or json output and that could result in a crash.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-5592-p365-24xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-40169
- https://github.com/ImageMagick/ImageMagick/commit/f86452a8aea37bf2b4bd36127f836dcc5f138b38
- https://github.com/ImageMagick/ImageMagick
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
