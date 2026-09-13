# [M] ImageMagick: Heap Buffer Over-Write in MIFF encoder when using LZMA compression

## Summary
Severity: Medium
Advisory: CVE-2026-46521
Aliases: GHSA-jcqp-6r6f-3mfx
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46521
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-48 and 7.1.2-23, when using LZMA compression in the MIFF encoder an out of bounds write can occur due to a missing check. This issue has been patched in versions 6.9.13-48 and 7.1.2-23.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46521.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-jcqp-6r6f-3mfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-46521
