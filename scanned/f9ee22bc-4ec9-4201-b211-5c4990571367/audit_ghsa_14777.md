# [M] Typo3 Cross-Site Scripting in Language Pack Handling

## Summary
Severity: Medium
Advisory: GHSA-259v-xm34-p7fr
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-259v-xm34-p7fr
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.4

## Details
Failing to properly encode information from external sources, language pack handling in the install tool is vulnerable to cross-site scripting.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-01-22-8.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-004
