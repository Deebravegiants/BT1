# [M] Authentication Bypass in TYPO3 CMS

## Summary
Severity: Medium
Advisory: GHSA-6xh8-8pfv-53vx
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-6xh8-8pfv-53vx
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.20
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.5
- Packagist: `typo3/cms` — affected >=8.0.0 <8.0.1

## Details
The default authentication service misses to invalidate empty strings as password. Therefore it is possible to authenticate backend and frontend users without password set in the database.
Note: TYPO3 does not allow to create user accounts without a password. Your TYPO3 installation might only be affected if there is a third party component creating user accounts without password by directly manipulating the database.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-04-12-3.yaml
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-011
