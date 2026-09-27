# [M] JLSEC-2026-1082

## Summary
Severity: Medium
Advisory: JLSEC-2026-1082
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1082
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2029+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions prior to 7.1.2-27, the BGR decoder does not check for an end-of-file in every location so a crafted image could result in an heap buffer over-read. This issue has been fixed in version 7.1.2-27.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7rgw-xg25-prjm
