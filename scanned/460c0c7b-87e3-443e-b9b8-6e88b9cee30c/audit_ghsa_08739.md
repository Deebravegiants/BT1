# [M] ImageMagick: Policy Bypass in MNG coder could 

## Summary
Severity: Medium
Advisory: GHSA-g5mf-wqq5-vwg6
CVE: CVE-2026-45664
CWE: CWE-400, CWE-407, CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-g5mf-wqq5-vwg6
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
Because of a missing check in the MNG coder it would be possible to read more images than the list limit policy would allow resulting in excessive resource use.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-g5mf-wqq5-vwg6
- https://nvd.nist.gov/vuln/detail/CVE-2026-45664
- https://github.com/ImageMagick/ImageMagick
