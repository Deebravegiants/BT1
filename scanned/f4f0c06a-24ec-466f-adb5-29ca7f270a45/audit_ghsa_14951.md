# [M] TYPO3 Broken Access Control in Localization Handling

## Summary
Severity: Medium
Advisory: GHSA-772m-43f3-hmf8
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-772m-43f3-hmf8
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.23

## Details
It has been discovered that backend users having limited access to specific languages are capable of modifying and creating pages in the default language which actually should be disallowed. A valid backend user account is needed in order to exploit this vulnerability.

## References
- https://github.com/TYPO3/typo3/commit/5004201ee77a69cb825637bc95cdeedb1186f4d4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-01-22-3.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-003
