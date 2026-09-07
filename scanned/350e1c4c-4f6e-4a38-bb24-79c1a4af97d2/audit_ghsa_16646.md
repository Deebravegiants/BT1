# [M] TYPO3 Brute Force Protection Bypass in backend login

## Summary
Severity: Medium
Advisory: GHSA-jqr8-q455-xx45
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-jqr8-q455-xx45
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.14
- Packagist: `typo3/cms` — affected >=7.0.0 <7.3.1

## Details
The backend login has a basic brute force protection implementation which pauses for 5 seconds if wrong credentials are given. This pause however could be bypassed by forging a special request, making brute force attacks on backend editor credentials more feasible.

## References
- https://github.com/TYPO3/typo3/commit/0b67290bbd941c07b0101bbfd6c7aadcbb93c75c
- https://github.com/TYPO3/typo3/commit/0f3fb37674688aba5a44ca6f5df7f8a327a5b5f6
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-07-01-5.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2015-006
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-006
