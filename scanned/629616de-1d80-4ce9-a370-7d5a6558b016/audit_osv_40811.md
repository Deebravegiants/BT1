# [M] ImageMagick: Infinite Loop in connected-components when providing invalid arguments

## Summary
Severity: Medium
Advisory: CVE-2026-55595
Aliases: GHSA-qhmf-7fc4-8q3h
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-55595
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-51 and 7.1.2-26, when providing invalid arguments to the connected-components option an infinite loop will occur. This issue has been fixed in versions 6.9.13-51 and 7.1.2-26.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55595.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-qhmf-7fc4-8q3h
- https://nvd.nist.gov/vuln/detail/CVE-2026-55595
