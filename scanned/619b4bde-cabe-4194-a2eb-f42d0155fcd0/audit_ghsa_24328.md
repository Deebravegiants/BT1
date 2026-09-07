# [H] TYPO3 doesn't properly check file extensions

## Summary
Severity: High
Advisory: GHSA-54jj-pxx2-pv8h
CVE: CVE-2013-4250
CWE: CWE-20, CWE-434
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-54jj-pxx2-pv8h
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.0.0 <6.0.8
- Packagist: `typo3/cms` — affected >=6.1.0 <6.1.3

## Details
The (1) file upload component and (2) File Abstraction Layer (FAL) in TYPO3 6.0.x before 6.0.8 and 6.1.x before 6.1.3 do not properly check file extensions, which allow remote authenticated editors to execute arbitrary PHP code by uploading a .php file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4250
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2013-002
