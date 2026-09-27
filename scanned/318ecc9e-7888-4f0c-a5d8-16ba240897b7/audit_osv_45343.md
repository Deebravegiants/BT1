# [M] JLSEC-2026-1034

## Summary
Severity: Medium
Advisory: JLSEC-2026-1034
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1034
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2028+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-51 and 7.1.2-26, an integer overflow in the XCF decoder can result in an out of bounds read when a crafted image is read, potentially resulting in a crash. This issue has been fixed in versions 6.9.13-51 and 7.1.2-26.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-pjxj-pchx-4c3m
