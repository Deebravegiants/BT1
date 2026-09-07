# [H] TYPO3 CMS: Destructive Actions on File Mount Folders

## Summary
Severity: High
Advisory: GHSA-3v8v-4wg6-r7qh
CVE: CVE-2026-47343
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-3v8v-4wg6-r7qh
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=0 <10.4.57
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.51
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.46
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.3.3

## Details
### Problem
Non-privileged backend users with file mount access were able to perform write operations (move, delete, rename) on folders representing the root of an active file mount due to missing authorization restrictions.

### Solution
Update to TYPO3 versions 10.4.57 ELTS, 11.5.51 ELTS, 12.4.46 ELTS, 13.4.31 LTS, 14.3.3 LTS that fix the problem described.

### Credits
TYPO3 CMS thanks Arne Uplegger for reporting this issue, and TYPO3 security team member Elias Häußler for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-007](https://typo3.org/security/advisory/typo3-core-sa-2026-007)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-3v8v-4wg6-r7qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-47343
- https://github.com/TYPO3/typo3/commit/504e72470ff72aaf5d2256878bf473747f389798
- https://github.com/TYPO3/typo3/commit/ac4125aef8b9b94528a7f74db2444db57b05a87b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-47343.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-007
