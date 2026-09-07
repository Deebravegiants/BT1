# [M] TYPO3 Frontend vulnerable to Unauthenticated Path Disclosure

## Summary
Severity: Medium
Advisory: GHSA-pqfv-97hj-g97g
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-pqfv-97hj-g97g
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.15
- Packagist: `typo3/cms` — affected >=7.0.0 <7.4.0

## Details
It has been discovered, that calling a PHP script which is delivered with TYPO3 for testing purposes, discloses the absolute server path to the TYPO3 installation.

## References
- https://github.com/TYPO3/typo3/commit/ed1e46f89c8e5f699ced245e873d0eff21e5c75e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-09-08-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2015-008
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-008
