# [M] ImageMagick: Heap Buffer Over-Write in fx operation

## Summary
Severity: Medium
Advisory: CVE-2026-62363
Aliases: GHSA-422r-8c97-xcg4
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-62363
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions prior to 7.1.2-27, a heap buffer over-write can occur in the fx operation by passing a crafted argument. This issue has been fixed in version 7.1.2-27.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62363.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-422r-8c97-xcg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-62363
