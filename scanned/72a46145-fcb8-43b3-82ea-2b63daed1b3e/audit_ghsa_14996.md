# [M] TYPO3 Cross-Site Scripting (XSS) in form component

## Summary
Severity: Medium
Advisory: GHSA-5j86-5xvg-7q93
Ecosystem: Packagist
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-5j86-5xvg-7q93
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.18

## Details
Failing to sanitize content from unauthenticated  website visitors, the form component is susceptible to Cross-Site Scripting.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-02-16-4.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-004
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2016-004
