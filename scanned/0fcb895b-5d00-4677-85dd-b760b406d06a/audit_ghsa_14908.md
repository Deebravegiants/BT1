# [M] SQL Injection in TYPO3 Frontend Login

## Summary
Severity: Medium
Advisory: GHSA-j86x-pjmr-9m6w
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-j86x-pjmr-9m6w
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.26
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.10

## Details
Failing to properly escape user input, the frontend login component is vulnerable to SQL Injection. A valid frontend user account is needed to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-07-19-3.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-016
