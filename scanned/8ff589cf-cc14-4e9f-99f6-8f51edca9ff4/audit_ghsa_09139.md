# [M] ImageMagick: Out-of-Bounds Read in connected components when the user supplies an invalid keep-top define

## Summary
Severity: Medium
Advisory: GHSA-vhrh-72hq-w8m7
CVE: CVE-2026-45359
CWE: CWE-125, CWE-129
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-vhrh-72hq-w8m7
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-OpenMP-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-OpenMP-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-OpenMP-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-OpenMP-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-OpenMP-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-arm64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-x64` — affected >=0 <14.13.1
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.13.1

## Details
An invalid `connected-components:keep-top` value could result in a heap buffer over-read when performing the connected components operation.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-vhrh-72hq-w8m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-45359
- https://github.com/ImageMagick/ImageMagick
