# [M] ImageMagick: Policy Bypass can read disallowed files via symlink

## Summary
Severity: Medium
Advisory: GHSA-xcjm-wqff-m669
CVE: CVE-2026-49219
CWE: CWE-200, CWE-22, CWE-78, CWE-863
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-xcjm-wqff-m669
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
An incorrect parsing of the filename can result in a policy bypass and read files disallowed by a security policy using a symlink.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-xcjm-wqff-m669
- https://nvd.nist.gov/vuln/detail/CVE-2026-49219
- https://github.com/ImageMagick/ImageMagick
