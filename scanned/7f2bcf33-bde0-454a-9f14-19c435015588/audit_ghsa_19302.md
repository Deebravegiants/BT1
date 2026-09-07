# [H] TYPO3 Allows Privilege Escalation to System Maintainer

## Summary
Severity: High
Advisory: GHSA-6frx-j292-c844
CVE: CVE-2025-47940
CWE: CWE-283
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-20
Source: https://github.com/advisories/GHSA-6frx-j292-c844
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=10.4.0 <10.4.50
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.44
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.31
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.12

## Details
### Problem
Administrator-level backend users without system maintainer privileges can escalate their privileges and gain system maintainer access. Exploiting this vulnerability requires a valid administrator account.

### Solution
Update to TYPO3 versions 10.4.50 ELTS, 11.5.44 ELTS, 12.4.31 LTS, 13.4.12 LTS that fix the problem described.

### Credits
Thanks to Alexander Künzl for reporting this issue, and to TYPO3 core & security team member Oliver Hader for fixing it.

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-6frx-j292-c844
- https://nvd.nist.gov/vuln/detail/CVE-2025-47940
- https://github.com/TYPO3-CMS/core/commit/a659cc8c0ae05c44dd7f01d13629cdd2d0b7219b
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2025-016
