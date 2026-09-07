# [M] Cross-Site Scripting (XSS) in TYPO3 component CSS styled content

## Summary
Severity: Medium
Advisory: GHSA-8j9v-4hhh-x43c
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-8j9v-4hhh-x43c
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.19
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.4

## Details
Failing to properly encode user input, the CSS styled content component is susceptible to Cross-Site Scripting, allowing authenticated editors to inject arbitrary HTML or JavaScript.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-02-23-3.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-007
