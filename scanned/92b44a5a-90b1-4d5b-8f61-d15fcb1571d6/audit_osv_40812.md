# [M] ImageMagick: Heap Buffer Over-Write in JP2 encoder when due to incorrect handling of arguments

## Summary
Severity: Medium
Advisory: CVE-2026-55597
Aliases: GHSA-c4v7-w88g-m6c4
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-55597
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-26, an incorrect handling of arguments can cause a heap buffer over-write in the JP2 encoder. This issue has been fixed in version7.1.2-26.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55597.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-c4v7-w88g-m6c4
- https://nvd.nist.gov/vuln/detail/CVE-2026-55597
