# [M] JLSEC-2026-1005

## Summary
Severity: Medium
Advisory: JLSEC-2026-1005
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1005
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-21 and 6.9.13-46, a malicious MIFF file could trigger an overflow when a user opens it in the display tool and right-clicks a tile to invoke the Load / Update menu item. This vulnerability is fixed in 7.1.2-21 and 6.9.13-46.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7mxf-ff4f-jj7p
