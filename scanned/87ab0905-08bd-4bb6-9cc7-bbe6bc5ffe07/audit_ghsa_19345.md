# [M] The Backup Plus extension for TYPO3 (ns_backup) allows command injections

## Summary
Severity: Medium
Advisory: GHSA-463c-jhp2-4mm7
CVE: CVE-2025-48204
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-463c-jhp2-4mm7
Type: github-advisory

## Affected
- Packagist: `nitsan/ns-backup` — affected >=0 <13.0.1

## Details
The ns_backup extension through 13.0.0 for TYPO3 allows command injection when creating a backup. An authenticated backend user with access to the extensions backend module is required to exploit the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48204
- https://github.com/nitsan-technologies/ns_backup/commit/67b8102a19e8e516dc4228f5c42f9e4fba5046cb
- https://github.com/nitsan-technologies/ns_backup
- https://typo3.org/security/advisory/typo3-ext-sa-2025-007
