# [M] Typo3 Improper Access Control

## Summary
Severity: Medium
Advisory: GHSA-qf79-34j4-54m6
CVE: CVE-2011-4904
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-qf79-34j4-54m6
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <4.4.9
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.4

## Details
TYPO3 before 4.4.9 and 4.5.x before 4.5.4 does not apply proper access control on ExtDirect calls which allows remote attackers to retrieve ExtDirect endpoint services.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4904
- https://github.com/TYPO3/typo3
- https://security-tracker.debian.org/tracker/CVE-2011-4904
- https://typo3.org/security/advisory/typo3-core-sa-2011-001/#Missing_Access_Control
