# [H] TYPO3 Arbitrary Shell Execution in Swiftmailer library

## Summary
Severity: High
Advisory: GHSA-45xg-4w5x-j429
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-45xg-4w5x-j429
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.6
- Packagist: `typo3/cms` — affected >=6.1.0 <6.1.12
- Packagist: `typo3/cms` — affected >=4.7.0 <4.7.20
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.37

## Details
The swiftmailer library in use allows to execute arbitrary shell commands if the "From" header comes from a non-trusted source and no "Return-Path" is configured. Affected are only TYPO3 installation the configuration option
```
$GLOBALS['TYPO3_CONF_VARS']['MAIL']['transport'] 
```
is set to "sendmail". Installations with the default configuration are not affected.

## References
- https://github.com/TYPO3/typo3/commit/313c4bba53dd78803a9ee97c1f6f1d450a521521
- https://github.com/TYPO3/typo3/commit/6af37574e063929eaab066dd9920b1fa8815da12
- https://github.com/TYPO3/typo3/commit/dbdd9f22b7cebf43f2e4abdb2a6a8a9f32af8f61
- https://github.com/TYPO3/typo3/commit/ead183c5acf25b7e1121adee5a5860bd9b5f05a2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2014-10-22-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2014-002
