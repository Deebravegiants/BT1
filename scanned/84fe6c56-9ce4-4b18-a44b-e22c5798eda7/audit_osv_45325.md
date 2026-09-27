# [H] ImageMagick is free and open-source software used for editing and manipulating digital images

## Summary
Severity: High
Advisory: JLSEC-2025-9
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/JLSEC-2025-9
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=7.1.1+0 <7.1.2001+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions prior to 7.1.2-0, infinite lines occur when writing during a specific XMP file conversion command. Version 7.1.2-0 fixes the issue.

## References
- https://drive.google.com/file/d/1iegkwlTjqnJTtM4XkiheYsjKsC6pxtId/view?usp=sharing
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-vmhh-8rxq-fp9g
