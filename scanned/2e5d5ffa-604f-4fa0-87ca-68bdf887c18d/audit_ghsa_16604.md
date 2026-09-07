# [H] TYPO3 CMS Authentication Bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-x4rj-f7m6-42c3
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-x4rj-f7m6-42c3
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.17
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.3.2
- Packagist: `typo3/cms-core` — affected >=7.0.0 <7.6.30

## Details
It has been discovered that TYPO3’s Salted Password system extension (which is a mandatory system component) is vulnerable to Authentication Bypass when using hashing methods which are related by PHP class inheritance. In standard TYPO3 core distributions stored passwords using the blowfish hashing algorithm can be overridden when using MD5 as the default hashing algorithm by just knowing a valid username. Per default the Portable PHP hashing algorithm (PHPass) is used which is not vulnerable.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/2018-07-12-1.yaml
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2018-001
