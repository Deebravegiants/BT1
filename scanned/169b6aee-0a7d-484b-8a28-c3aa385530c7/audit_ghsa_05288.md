# [H] ImageMagick: Policy Bypass in DCM decoder could result in image with invalid dimensions

## Summary
Severity: High
Advisory: GHSA-8pj9-6897-74xc
CVE: CVE-2026-49218
CWE: CWE-20
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-8pj9-6897-74xc
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
A missing check in the DCM decoder could result in an image with invalid dimensions and that could cause crashes in other operations.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-8pj9-6897-74xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-49218
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.14.0
