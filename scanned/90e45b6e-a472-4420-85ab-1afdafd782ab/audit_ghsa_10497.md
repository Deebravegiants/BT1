# [H] ImageMagick has a Stack Overflow in DestroyXMLTree()

## Summary
Severity: High
Advisory: GHSA-fwvm-ggf6-2p4x
CVE: CVE-2026-33908
CWE: CWE-674
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-fwvm-ggf6-2p4x
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
Magick frees the memory of the XML tree via the `DestroyXMLTree` function; however, this process is executed recursively with no depth limit imposed. When magick processes an XML file with deeply nested structures, it will exhaust the stack memory, resulting in a Denial of Service (DoS) attack.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-fwvm-ggf6-2p4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-33908
- https://github.com/ImageMagick/ImageMagick/commit/ccdc01180276aa2cb3d4a32a611aa4f417061cd8
- https://github.com/ImageMagick/ImageMagick
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
