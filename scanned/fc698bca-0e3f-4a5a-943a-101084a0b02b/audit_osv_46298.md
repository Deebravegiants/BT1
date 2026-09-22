# [M] JLSEC-2026-989

## Summary
Severity: Medium
Advisory: JLSEC-2026-989
Ecosystem: Julia
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-989
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-16 and 6.9.13-41, when a memory allocation fails in the sixel encoder it would be possible to write past the end of a buffer on the stack. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-49hx-7656-jpg3
