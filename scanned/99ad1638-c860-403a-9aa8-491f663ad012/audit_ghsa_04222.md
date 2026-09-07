# [M] TYPO3 CMS: Broken Access Control in Media Module

## Summary
Severity: Medium
Advisory: GHSA-q93m-25xv-94hh
CVE: CVE-2026-47351
CWE: CWE-200, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-q93m-25xv-94hh
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=0 <10.4.57
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.51
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.46
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.3.3
- Packagist: `typo3/cms-backend` — affected >=0 <10.4.57
- Packagist: `typo3/cms-backend` — affected >=11.0.0 <11.5.51
- Packagist: `typo3/cms-backend` — affected >=12.0.0 <12.4.46
- Packagist: `typo3/cms-backend` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-backend` — affected >=14.0.0 <14.3.3

## Details
### Problem
Backend users were able to insert arbitrary records and files into the TYPO3 clipboard without proper read permission checks, which allowed users to gather information about records and files they were not authorized to view.

### Solution
Update to TYPO3 versions 10.4.57 ELTS, 11.5.51 ELTS, 12.4.46 ELTS, 13.4.31 LTS, 14.3.3 LTS that fix the problem described.

### Credits
TYPO3 CMS thanks Vincent Yang for reporting this issue, and to TYPO3 security team member Elias Häußler for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-014](https://typo3.org/security/advisory/typo3-core-sa-2026-014)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-q93m-25xv-94hh
- https://nvd.nist.gov/vuln/detail/CVE-2026-47351
- https://github.com/TYPO3/typo3/commit/2740707563343d78184c0b7c6303a7484553d7f3
- https://github.com/TYPO3/typo3/commit/932fbb9fcea25094e8bcc0f0ec5aab56b1d92451
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-47351.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-014
