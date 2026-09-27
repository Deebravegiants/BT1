# [M] ImageMagick: Integer Overflow in JNX decoder causes heap buffer over-write when processing extremly large files on 32-bit builds

## Summary
Severity: Medium
Advisory: GHSA-h22j-f9xw-xjjm
CVE: CVE-2026-62946
CWE: CWE-190
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-h22j-f9xw-xjjm
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.15.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.15.0

## Details
When processing an extremely large JNX file on 32-bit platforms an integer overflow will happen that can cause a heap buffer over-write.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-h22j-f9xw-xjjm
- https://github.com/ImageMagick/ImageMagick
- https://github.com/dlemstra/Magick.NET/releases/tag/14.15.0
