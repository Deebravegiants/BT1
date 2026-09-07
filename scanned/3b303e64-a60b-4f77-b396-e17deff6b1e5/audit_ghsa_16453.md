# [M] TYPO3 Information Disclosure Vulnerability Exploitable by Editors

## Summary
Severity: Medium
Advisory: GHSA-r287-hc8j-w56h
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-r287-hc8j-w56h
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.14
- Packagist: `typo3/cms` — affected >=7.0.0 <7.3.1

## Details
It has been discovered, that editors with access to the file list module could list all files names and folder names in the root directory of a TYPO3 installation. Modification of files, listing further nested directories or retrieving file contents was not possible. A valid backend user account is needed to exploit this vulnerability.

## References
- https://github.com/TYPO3/typo3/commit/d9caccb26c954834e7d43fbbe84a3130cc95524a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-07-01-4.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2015-005
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-005
