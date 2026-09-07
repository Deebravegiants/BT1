# [M] TYPO3 CMS has an Open Redirect Vulnerability via Core Utilities

## Summary
Severity: Medium
Advisory: GHSA-3p42-w5ch-gg42
CVE: CVE-2026-47347
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-3p42-w5ch-gg42
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=0 <10.4.57
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.51
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.46
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.3.3

## Details
### Problem
Applications that use `GeneralUtility::sanitizeLocalUrl` to allow only local URLs are vulnerable to open redirect attacks if the URL is used after it has passed the aforementioned sanitization checks. This enables attackers to redirect users to external content and carry out phishing attacks.

### Solution
Update to TYPO3 versions 10.4.57 ELTS, 11.5.51 ELTS, 12.4.46 ELTS, 13.4.31 LTS, 14.3.3 LTS that fix the problem described.

### Credits
TYPO3 CMS thanks Alexandre Romao for reporting this issue, and TYPO3 core & security team member Benjamin Franzke for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-009](https://typo3.org/security/advisory/typo3-core-sa-2026-009)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-3p42-w5ch-gg42
- https://nvd.nist.gov/vuln/detail/CVE-2026-47347
- https://github.com/TYPO3/typo3/commit/22c2dd5398ebc4cb7aa4aa37e02cb39181dee0cd
- https://github.com/TYPO3/typo3/commit/3ffc0835012c6199db0e1dc4b56a77147d8600e0
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-47347.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-009
