# [H] TYPO3 Insecure Deserialization in Query Generator & Query View

## Summary
Severity: High
Advisory: GHSA-rcgc-4xfc-564v
CVE: CVE-2019-19849
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rcgc-4xfc-564v
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.2.1
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.12
- Packagist: `typo3/cms` — affected >=10.0.0 <10.2.1
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.12

## Details
An issue was discovered in TYPO3 before 8.7.30, 9.x before 9.5.12, and 10.x before 10.2.2. It has been discovered that the classes QueryGenerator and QueryView are vulnerable to insecure deserialization. One exploitable scenario requires having the system extension ext:lowlevel (Backend Module: DB Check) installed, with a valid backend user who has administrator privileges. The other exploitable scenario requires having the system extension ext:sys_action installed, with a valid backend user who has limited privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19849
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2019-19849.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2019-19849.yaml
- https://review.typo3.org/q/%2522Resolves:+%252389005%2522+topic:security
- https://typo3.org/security/advisory/typo3-core-sa-2019-026
