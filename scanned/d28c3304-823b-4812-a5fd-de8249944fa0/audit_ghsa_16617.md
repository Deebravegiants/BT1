# [M] TYPO3 Information Disclosure in Page Tree

## Summary
Severity: Medium
Advisory: GHSA-wvvp-jwf5-qcpc
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-wvvp-jwf5-qcpc
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.6

## Details
It has been discovered backend users not having read access to specific pages still could see them in the page tree which actually should be disallowed. A valid backend user account is needed in order to exploit this vulnerability.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/2019-05-07-4.yaml
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2019-009
