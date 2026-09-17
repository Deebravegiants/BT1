# [M] JLSEC-2026-1003

## Summary
Severity: Medium
Advisory: JLSEC-2026-1003
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1003
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2023+0

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Versions below 7.1.2-19 and 6.9.13-44 contain a heap use-after-free vulnerability that can cause a crash when reading and printing values from an invalid XMP profile. This issue has been fixed in versions 6.9.13-44 and 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/commit/5facfecf1abb3fed46a08f614dcc43d1e548e20d
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-r83h-crwp-3vm7
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
