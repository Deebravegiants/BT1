# [M] JLSEC-2026-1001

## Summary
Severity: Medium
Advisory: JLSEC-2026-1001
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1001
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions below 7.1.2-19, the JXL encoder has an heap write overflow when a user specifies that the image should be encoded as 16 bit floats. This issue has been fixed in version 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-jvgr-9ph5-m8v4
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
