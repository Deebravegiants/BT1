# [M] ImageMagick has an Out-of-Bounds write of a zero byte in its X11 display interaction

## Summary
Severity: Medium
Advisory: CVE-2026-33535
Aliases: GHSA-mw3m-pqr2-qv7c
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33535
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-18 and 6.9.13-43, an out-of-bounds write of a zero byte exists in the X11 `display` interaction path that could lead to a crash. Versions 7.1.2-18 and 6.9.13-43 patch the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33535.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-mw3m-pqr2-qv7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33535
