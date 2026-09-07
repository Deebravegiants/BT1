# [M] Cross-Site Scripting in Content Preview

## Summary
Severity: Medium
Advisory: GHSA-fjh3-g8gq-9q92
CVE: CVE-2021-21340
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-fjh3-g8gq-9q92
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-backend` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms` — affected >=11.0.0 <11.1.1

## Details
### Problem
It has been discovered that database fields used as _descriptionColumn_ are vulnerable to cross-site scripting when their content gets previewed in the page module. A valid backend user account is needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 10.4.14, 11.1.1 that fix the problem described.

### Credits
Thanks to Richie Lee who reported this issue and to TYPO3 framework merger Andreas Fernandez who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-007](https://typo3.org/security/advisory/typo3-core-sa-2021-007)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-fjh3-g8gq-9q92
- https://nvd.nist.gov/vuln/detail/CVE-2021-21340
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-21340.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-21340.yaml
- https://packagist.org/packages/typo3/cms-backend
- https://typo3.org/security/advisory/typo3-core-sa-2021-007
