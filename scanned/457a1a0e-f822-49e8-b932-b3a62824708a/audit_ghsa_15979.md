# [M] Path traversal in redaxo

## Summary
Severity: Medium
Advisory: GHSA-37gm-h5wr-pf25
CVE: CVE-2024-46212
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-16
Source: https://github.com/advisories/GHSA-37gm-h5wr-pf25
Type: github-advisory

## Affected
- Packagist: `redaxo/source` — affected >=0

## Details
An issue in the component /index.php?page=backup/export of REDAXO CMS v5.17.1 allows attackers to execute a directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46212
- https://github.com/Purposex7/Vulns4Study/blob/main/REDAXO%20File%20Download%20Exploit.md
- https://github.com/redaxo/redaxo
