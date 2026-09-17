# [M] JLSEC-2026-993

## Summary
Severity: Medium
Advisory: JLSEC-2026-993
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-993
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions below 7.1.2-189 and 6.9.13-44, when `Magick` parses an XML file it is possible that a single zero byte is written out of the bounds. This issue has been fixed in versions 6.9.13-44 and 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/commit/ae679e2fd19ec656bfab9f822ae4cf06bf91604d
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-cr67-pvmx-2pp2
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
