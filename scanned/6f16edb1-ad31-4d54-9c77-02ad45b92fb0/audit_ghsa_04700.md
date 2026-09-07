# [M] TYPO3 CMS has Broken Access Control in its DataHandler

## Summary
Severity: Medium
Advisory: GHSA-qcmw-6rm2-5x78
CVE: CVE-2026-47350
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-qcmw-6rm2-5x78
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.3.3

## Details
### Problem
Backend users were able to move records to a different page without having edit permissions on the source page.

### Solution
Update to TYPO3 versions 13.4.31 LTS, 14.3.3 LTS that fix the problem described.

### Credits
TYPO3 CMS thanks Hyunseo Shin for reporting this issue, and TYPO3 security team member Torben Hansen for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-012](https://typo3.org/security/advisory/typo3-core-sa-2026-012)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-qcmw-6rm2-5x78
- https://nvd.nist.gov/vuln/detail/CVE-2026-47350
- https://github.com/TYPO3/typo3/commit/195356996a60e40aeb2cd3e45a5f5c8940d5e116
- https://github.com/TYPO3/typo3/commit/c9898d2e67608eda78f8bd1f06ee9cf05a872a56
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-47350.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-012
