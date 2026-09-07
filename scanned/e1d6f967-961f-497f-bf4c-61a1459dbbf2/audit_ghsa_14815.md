# [M] TYPO3 Cross-Site Scripting in Filelist Module

## Summary
Severity: Medium
Advisory: GHSA-g7hw-jh4p-75wr
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-g7hw-jh4p-75wr
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=10.0.0 <10.2.1
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.12

## Details
It has been discovered that the output table listing in the “Files” backend module is vulnerable to cross-site scripting when a file extension contains malicious sequences.

Access to the file system of the server - either directly or through synchronization - is required to exploit the vulnerability.

## References
- https://github.com/TYPO3/typo3/commit/044d7dbe28382919c765b6b815d420f480a1ac70
- https://github.com/TYPO3/typo3/commit/96b122b756cc778697845d48210b0993c0724b5f
- https://github.com/TYPO3/typo3/commit/fcc1bab07027ba9d8140a91006d3cda1244d6298
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-12-17-3.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-023
