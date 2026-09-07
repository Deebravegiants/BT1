# [M] Path Traversal in TYPO3 Core

## Summary
Severity: Medium
Advisory: GHSA-gj48-w74w-8gvm
Ecosystem: Packagist
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-gj48-w74w-8gvm
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.29
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.13
- Packagist: `typo3/cms` — affected >=8.0.0 <8.4.1

## Details
Due to a too loose type check in an API method, attackers could bypass the directory traversal check by providing an invalid UTF-8 encoding sequence.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-11-22-2.yaml
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-024
