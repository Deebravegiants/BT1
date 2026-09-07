# [M] Open Redirection in Login Handling

## Summary
Severity: Medium
Advisory: GHSA-4jhw-2p6j-5wmp
CVE: CVE-2021-21338
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-4jhw-2p6j-5wmp
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=6.2.0 <6.2.57
- Packagist: `typo3/cms-core` — affected >=7.0.0 <7.6.51
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.40
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.25
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.25

## Details
### Problem
It has been discovered that Login Handling is susceptible to open redirection which allows attackers redirecting to arbitrary content, and conducting phishing attacks. No authentication is required in order to exploit this vulnerability.

### Solution
Update to TYPO3 versions 6.2.57, 7.6.51, 8.7.40, 9.5.25, 10.4.14, 11.1.1 that fix the problem described.

### Credits
Thanks to Alexander Kellner who reported this issue and to TYPO3 security team member Torben Hansen who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-001](https://typo3.org/security/advisory/typo3-core-sa-2021-001)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-4jhw-2p6j-5wmp
- https://nvd.nist.gov/vuln/detail/CVE-2021-21338
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-21338.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-21338.yaml
- https://packagist.org/packages/typo3/cms-core
- https://typo3.org/security/advisory/typo3-core-sa-2021-001
