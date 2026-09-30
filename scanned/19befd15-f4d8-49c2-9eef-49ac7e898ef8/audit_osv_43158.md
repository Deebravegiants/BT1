# [C] dulldusk phpfm - Missing Authentication by Default Allows Full Filesystem Access

## Summary
Severity: Critical
Advisory: CVE-2026-72593
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72593
Type: osv

## Details
A missing authentication vulnerability in dulldusk/phpfm through 1.8.0 allows an unauthenticated remote attacker to access the full file manager functionality including reading, writing, deleting, and uploading files anywhere on the server filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72593.json
- https://github.com/dulldusk/phpfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-72593
- https://github.com/dulldusk/phpfm/blob/master/index.php
