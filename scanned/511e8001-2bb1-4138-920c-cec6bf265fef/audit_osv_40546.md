# [M] ImageMagick: Heap Buffer Over-Write in SF3 encoder when writing multi-frame image

## Summary
Severity: Medium
Advisory: CVE-2026-53465
Aliases: GHSA-44cp-c3ww-9rv5
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-53465
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-25, a crafted multi-frame can result in a heap buffer over-write when encoding it with the SF3 encoder. This issue has been patched in version 7.1.2-25.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53465.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-44cp-c3ww-9rv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53465
