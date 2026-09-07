# [M] TYPO3 CMS has Cross-Site Scripting in Indexed Search

## Summary
Severity: Medium
Advisory: GHSA-cg75-qfg2-w9hj
CVE: CVE-2026-47348
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-cg75-qfg2-w9hj
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.3.3
- Packagist: `typo3/cms-indexed-search` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-indexed-search` — affected >=14.0.0 <14.3.3

## Details
### Problem
Editors with access to create or modify page content were able to include HTML markup in page titles that were stored in the search index without sanitization. When displayed in frontend search results via the Indexed Search plugin, these titles were rendered without proper output encoding, resulting in a Cross-Site Scripting vulnerability.

### Solution
Update to TYPO3 versions 13.4.31 LTS, 14.3.3 LTS that fix the problem described.

### Credits
TYPO3 CMS thanks Jan Kahmen and Sanjay Singh Jhala for reporting this issue, and to TYPO3 core & security team member Oliver Hader for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-010](https://typo3.org/security/advisory/typo3-core-sa-2026-010)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-cg75-qfg2-w9hj
- https://nvd.nist.gov/vuln/detail/CVE-2026-47348
- https://github.com/TYPO3/typo3/commit/2e96dd0e9fab7ad877b741fb9f6fc645b4270a3e
- https://github.com/TYPO3/typo3/commit/8004b91a5951cfe01dda8554f77d0daa82d6b899
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-47348.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-010
