# [M] ImageMagick: Stack overflow in fx operation

## Summary
Severity: Medium
Advisory: CVE-2026-46557
Aliases: GHSA-rcr6-g7jc-f57g
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46557
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-23, due to a missing depth check a stack overflow can occur in the fx operation by passing a crafted argument. This issue has been patched in version 7.1.2-23.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46557.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-rcr6-g7jc-f57g
- https://nvd.nist.gov/vuln/detail/CVE-2026-46557
