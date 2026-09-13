# [M] JLSEC-2026-1037

## Summary
Severity: Medium
Advisory: JLSEC-2026-1037
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1037
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2028+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-51 and 7.1.2-26, a heap buffer overflow occurs in the MVG decoder that could result in an out of bounds write when processing a crafted image. This issue has been fixed in versions 6.9.13-51 and 7.1.2-26.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wx47-rm3x-jx6p
