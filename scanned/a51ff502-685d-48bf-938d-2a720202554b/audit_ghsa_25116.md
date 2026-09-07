# [M] TYPO3 Directory Traversal on ZIP extraction

## Summary
Severity: Medium
Advisory: GHSA-77p4-wfr8-977w
CVE: CVE-2019-19848
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-77p4-wfr8-977w
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.2.2
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.12
- Packagist: `typo3/cms` — affected >=10.0.0 <10.2.2
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.12

## Details
An issue was discovered in TYPO3 before 8.7.30, 9.x before 9.5.12, and 10.x before 10.2.2. It has been discovered that the extraction of manually uploaded ZIP archives in Extension Manager is vulnerable to directory traversal. Admin privileges are required in order to exploit this vulnerability. (In v9 LTS and later, System Maintainer privileges are also required.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19848
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2019-19848.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2019-19848.yaml
- https://review.typo3.org/q/%2522Resolves:+%252388764%2522+topic:security
- https://typo3.org/security/advisory/typo3-core-sa-2019-024
