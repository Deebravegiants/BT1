# [H] Insecure Deserialization & Arbitrary Code Execution in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-ppgf-8745-8pgx
CWE: CWE-502
Ecosystem: Packagist
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-ppgf-8745-8pgx
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.30
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.17
- Packagist: `typo3/cms` — affected >=9.0.0 <9.3.2

## Details
Phar files (formerly known as "PHP archives") can act als self extracting archives which leads to the fact that source code is executed when Phar files are invoked. The Phar file format is not limited to be stored with a dedicated file extension - "bundle.phar" would be valid as well as "bundle.txt" would be. This way, Phar files can be obfuscated as image or text file which would not be denied from being uploaded and persisted to a TYPO3 installation. Due to a missing sanitization of user input, those Phar files can be invoked by manipulated URLs in TYPO3 backend forms. A valid backend user account is needed to exploit this vulnerability. In theory the attack vector would be possible in the TYPO3 frontend as well, however no functional exploit has been identified so far.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-07-12-2.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2018-002
