# [C] cube-root directory-serve - Unauthenticated Path Traversal Arbitrary File Deletion

## Summary
Severity: Critical
Advisory: CVE-2026-72569
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72569
Type: osv

## Details
A path traversal vulnerability in cube-root/directory-serve through 1.3.7 allows an unauthenticated remote attacker to delete arbitrary files outside the intended served directory when the application is run with the --delete option.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72569.json
- https://github.com/cube-root/directory-serve
- https://nvd.nist.gov/vuln/detail/CVE-2026-72569
- https://github.com/cube-root/directory-serve/blob/main/lib/middleware/file-remove.js
