# [M] Information Disclosure in TYPO3 CMS

## Summary
Severity: Medium
Advisory: GHSA-g46h-v2cc-6c94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-g46h-v2cc-6c94
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.22
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.5

## Details
Failing to properly check user permission on file storages, editors could gain knowledge of protected storages and its folders as well as using them in a file collection being rendered in the frontend. A valid backend user account is needed to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2017-09-05-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2017-005
