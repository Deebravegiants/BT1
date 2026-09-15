# [M] ImageMagick: Policy Bypass in concatenate operation due to missing checks

## Summary
Severity: Medium
Advisory: GHSA-82mp-vp5c-9pf7
CVE: CVE-2026-55628
CWE: CWE-73, CWE-862
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-82mp-vp5c-9pf7
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
The `-concatenate` operation is missing policy checks and that could result in both reading and writing to paths disallowed by the security policy.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-82mp-vp5c-9pf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-55628
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.15.0
