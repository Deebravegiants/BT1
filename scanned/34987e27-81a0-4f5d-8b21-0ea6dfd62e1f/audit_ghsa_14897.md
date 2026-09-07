# [M] Cross-Site Scripting in third party library mso/idna-convert

## Summary
Severity: Medium
Advisory: GHSA-qmwf-j7g7-f5jw
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-qmwf-j7g7-f5jw
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.10
- Packagist: `typo3/cms` — affected >=8.0.0 <8.2.1

## Details
Make sure to not expose the vendor directory to the publicly accessible document root. In composer managed installation, make sure to configure a dedicated web folder. In general it is recommended to not expose the complete typo3_src sources folder in the document root.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-07-19-7.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2016-020
