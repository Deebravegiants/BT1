# [M] ImageMagick: Policy Bypass in PSD decoder

## Summary
Severity: Medium
Advisory: GHSA-cwpj-h54c-xjpx
CVE: CVE-2026-45031
CWE: CWE-400, CWE-770
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-cwpj-h54c-xjpx
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
Due to a missing check in the PSD decoder it would be possible to bypass the `list-length` resource policy when decoding a PSD image. Other security limits would still apply.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-cwpj-h54c-xjpx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45031
- https://github.com/ImageMagick/ImageMagick
