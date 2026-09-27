# [M] ImageMagick: Heap Buffer Over-Write of a single byte in the JP2 encoder.

## Summary
Severity: Medium
Advisory: GHSA-533m-3wf6-c33v
CVE: CVE-2026-46559
CWE: CWE-193, CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-533m-3wf6-c33v
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
An incorrect check in the JP2 will result in an heap buffer over-write of a single byte when specifying certain options.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-533m-3wf6-c33v
- https://nvd.nist.gov/vuln/detail/CVE-2026-46559
- https://github.com/ImageMagick/ImageMagick
