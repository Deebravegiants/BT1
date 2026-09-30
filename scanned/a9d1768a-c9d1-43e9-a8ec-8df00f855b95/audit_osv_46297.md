# [M] JLSEC-2026-980

## Summary
Severity: Medium
Advisory: JLSEC-2026-980
Ecosystem: Julia
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-980
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-16 and 6.9.13-41, MAT decoder uses 32-bit arithmetic due to incorrect parenthesization resulting in a heap over-read. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-mrmj-x24c-wwcv
