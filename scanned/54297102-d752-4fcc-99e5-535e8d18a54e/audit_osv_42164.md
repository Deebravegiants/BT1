# [M] ImageMagick: Heap Buffer Over-Read in BGR decoder due to mising end-of-file check

## Summary
Severity: Medium
Advisory: CVE-2026-64685
Aliases: GHSA-7rgw-xg25-prjm
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-64685
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions prior to 7.1.2-27, the BGR decoder does not check for an end-of-file in every location so a crafted image could result in an heap buffer over-read. This issue has been fixed in version 7.1.2-27.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64685.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-7rgw-xg25-prjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-64685
