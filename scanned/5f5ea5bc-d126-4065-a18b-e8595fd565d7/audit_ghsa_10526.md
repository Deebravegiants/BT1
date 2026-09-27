# [M] ImageMagick has a heap overflow caused by integer overflow/wraparound in viff encoder on 32-bit builds

## Summary
Severity: Medium
Advisory: GHSA-v67w-737x-v2c9
CVE: CVE-2026-33900
CWE: CWE-190
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-13
Source: https://github.com/advisories/GHSA-v67w-737x-v2c9
Type: github-advisory

## Affected
- NuGet: `Magick.NET-Q16-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-HDRI-x86` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q16-x86` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-AnyCPU` — affected >=0 <14.12.0
- NuGet: `Magick.NET-Q8-x86` — affected >=0 <14.12.0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions below both 7.1.2-19 and 6.9.13-44, the viff encoder contains an integer truncation/wraparound issue on 32-bit builds that could trigger an out of bounds heap write, potentially causing a crash. This issue has been fixed in versions 6.9.13-44 and 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-v67w-737x-v2c9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33900
- https://github.com/ImageMagick/ImageMagick/commit/d27b840a61b322419a66d0d192ff56d52498148d
- https://github.com/ImageMagick/ImageMagick
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
