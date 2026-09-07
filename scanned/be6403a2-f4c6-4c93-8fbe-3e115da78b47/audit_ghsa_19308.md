# [H] The Backup Plus extension for TYPO3 (ns_backup) has a Predictable Resource Location

## Summary
Severity: High
Advisory: GHSA-hq4f-5qjv-fwrg
CVE: CVE-2025-48201
CWE: CWE-425
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-hq4f-5qjv-fwrg
Type: github-advisory

## Affected
- Packagist: `nitsan/ns-backup` — affected >=0 <13.0.1

## Details
The ns_backup extension through 13.0.0 for TYPO3 has a Predictable Resource Location. This allows an unauthenticated remote user to download created backups and configuration files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48201
- https://github.com/nitsan-technologies/ns_backup/commit/67b8102a19e8e516dc4228f5c42f9e4fba5046cb
- https://github.com/FriendsOfPHP/security-advisories/blob/master/nitsan/ns-backup/CVE-2025-48201.yaml
- https://github.com/nitsan-technologies/ns_backup
- https://typo3.org/security/advisory/typo3-ext-sa-2025-007
