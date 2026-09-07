# [M] Multiple Cross-Site Scripting vulnerabilities in TYPO3 backend

## Summary
Severity: Medium
Advisory: GHSA-5cxf-xx9j-54jc
Ecosystem: Packagist
Published: 2024-06-03
Source: https://github.com/advisories/GHSA-5cxf-xx9j-54jc
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.16
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.1

## Details
Failing to properly encode user input, several backend components are susceptible to Cross-Site Scripting, allowing authenticated editors to inject arbitrary HTML or JavaScript.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2015-12-15-1.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2015-011
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2015-011
