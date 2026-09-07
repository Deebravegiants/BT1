# [M] Cross-Site Scripting (XSS) vulnerability in typolinks

## Summary
Severity: Medium
Advisory: GHSA-p5c5-gmj4-g48f
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-p5c5-gmj4-g48f
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.26
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.10
- Packagist: `typo3/cms` — affected >=8.0.0 <8.2.1

## Details
All link fields within the TYPO3 installation are vulnerable to Cross-Site Scripting as authorized editors can insert data commands by using the url scheme "data:".

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-07-19-5.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2016-018
