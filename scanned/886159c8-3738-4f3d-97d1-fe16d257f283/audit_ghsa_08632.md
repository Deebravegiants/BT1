# [M] ImageMagick: Race Condition in distributed pixel cache server can result in file descriptor hijacking

## Summary
Severity: Medium
Advisory: GHSA-4g75-9r48-jf92
CVE: CVE-2026-46693
CWE: CWE-362, CWE-567
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-4g75-9r48-jf92
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
An attacker who can connect to a magick -distribute-cache service can hijack a file descriptor in the server process when a race condition is met.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-4g75-9r48-jf92
- https://nvd.nist.gov/vuln/detail/CVE-2026-46693
- https://github.com/ImageMagick/ImageMagick
