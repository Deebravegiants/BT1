# [M] Typo3 Information Disclosure in User Authentication

## Summary
Severity: Medium
Advisory: GHSA-m96r-7vqm-j95g
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-m96r-7vqm-j95g
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.6

## Details
It has been discovered that login failures have been logged on the default stream with log level "warning" including plain-text user credentials.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-05-07-5.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-010
