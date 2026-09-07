# [H] TYPO3 vulnerable to remote authenticated arbitrary code execution

## Summary
Severity: High
Advisory: GHSA-m76j-69c2-c3m8
CVE: CVE-2013-4321
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m76j-69c2-c3m8
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.0.0 <6.0.9
- Packagist: `typo3/cms` — affected >=6.1.0 <6.1.4

## Details
The File Abstraction Layer (FAL) in TYPO3 6.0.x before 6.0.9 and 6.1.x before 6.1.4 allows remote authenticated editors to execute arbitrary PHP code via unspecified characters in the file extension when renaming a file.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2013-4250.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4321
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2013-003
