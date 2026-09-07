# [M] TYPO3  SQL Injection in low-level Query Generator

## Summary
Severity: Medium
Advisory: GHSA-59pj-7mjh-4465
CVE: CVE-2019-19850
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-59pj-7mjh-4465
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=8.0 <8.7.30
- Packagist: `typo3/cms` — affected >=9.0 <9.5.12
- Packagist: `typo3/cms` — affected >=10.0 <10.2.2
- Packagist: `typo3/cms-core` — affected >=8.0 <8.7.30
- Packagist: `typo3/cms-core` — affected >=9.0 <9.5.12
- Packagist: `typo3/cms-core` — affected >=10.0 <10.2.2

## Details
An issue was discovered in TYPO3 before 8.7.30, 9.x before 9.5.12, and 10.x before 10.2.2. Because escaping of user-submitted content is mishandled, the class QueryGenerator is vulnerable to SQL injection. Exploitation requires having the system extension ext:lowlevel installed, and a valid backend user who has administrator privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19850
- https://github.com/TYPO3/typo3
- https://review.typo3.org/q/%2522Resolves:+%252389452%2522+topic:security
- https://typo3.org/security/advisory/typo3-core-sa-2019-025
