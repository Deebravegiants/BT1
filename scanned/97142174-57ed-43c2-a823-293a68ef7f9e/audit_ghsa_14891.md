# [M] TYPO3 is susceptible to Cross-Site Flashing

## Summary
Severity: Medium
Advisory: GHSA-qrxh-46mr-pr7q
Ecosystem: Packagist
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-qrxh-46mr-pr7q
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.16

## Details
The flashplayer misses to validate flash and image files. Therefore it is possible to embed flash videos from external domains.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-12-15-4.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2015-014
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-014
