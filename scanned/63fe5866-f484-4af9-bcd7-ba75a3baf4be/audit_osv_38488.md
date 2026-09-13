# [M] ImageMagick: Heap out-of-bounds write in JP2 encoder

## Summary
Severity: Medium
Advisory: CVE-2026-40310
Aliases: GHSA-pwg5-6jfc-crvh
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-40310
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Versions below both 7.1.2-19 and 6.9.13-44, contain a heap out-of-bounds write in the JP2 encoder with when a user specifies an invalid sampling index. This issue has been fixed in versions 6.9.13-44 and 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40310.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-pwg5-6jfc-crvh
- https://nvd.nist.gov/vuln/detail/CVE-2026-40310
- https://github.com/ImageMagick/ImageMagick/commit/3d653bea2df085c728a1c8f775808e1e9249dff9
