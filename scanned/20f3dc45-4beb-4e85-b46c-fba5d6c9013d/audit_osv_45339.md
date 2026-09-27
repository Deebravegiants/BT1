# [M] JLSEC-2026-1002

## Summary
Severity: Medium
Advisory: JLSEC-2026-1002
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1002
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Versions below both 7.1.2-19 and 6.9.13-44, contain a heap out-of-bounds write in the JP2 encoder with when a user specifies an invalid sampling index. This issue has been fixed in versions 6.9.13-44 and 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/commit/3d653bea2df085c728a1c8f775808e1e9249dff9
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-pwg5-6jfc-crvh
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
