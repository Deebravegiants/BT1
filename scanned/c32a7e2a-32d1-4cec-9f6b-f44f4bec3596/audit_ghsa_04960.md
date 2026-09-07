# [M] TYPO3 CMS has Broken Access Control in Backend API

## Summary
Severity: Medium
Advisory: GHSA-2j54-93q2-3hjq
CVE: CVE-2026-47352
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-2j54-93q2-3hjq
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
Authenticated backend users were able to retrieve file metadata via several Backend API routes without proper permission checks, allowing access to files outside their permitted file mounts or storages.

### Solution
Update to TYPO3 versions 10.4.57 ELTS, 11.5.51 ELTS, 12.4.46 ELTS, 13.4.31 LTS, 14.3.3 LTS that fix the problem described.

### Credits
TYPO3 CMS thanks Phong Lan for reporting this issue, and to TYPO3 core & security team member Oliver Hader for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-015](https://typo3.org/security/advisory/typo3-core-sa-2026-015)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-2j54-93q2-3hjq
- https://nvd.nist.gov/vuln/detail/CVE-2026-47352
- https://github.com/TYPO3/typo3/commit/17a3b7830d5931725db5fdab0cfc76d479884c96
- https://github.com/TYPO3/typo3/commit/bfe7c354168f467726020ed49299dd209a455719
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-47352.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-015
