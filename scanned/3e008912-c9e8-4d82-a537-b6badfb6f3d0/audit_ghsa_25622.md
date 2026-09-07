# [H] TYPO3 SQL injection vulnerability on the backend

## Summary
Severity: High
Advisory: GHSA-4rvc-5hrh-qmwf
CVE: CVE-2010-3662
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-4rvc-5hrh-qmwf
Type: github-advisory

## Affected
- Packagist: `typo3/cms-backend` — affected >=0 <4.1.14
- Packagist: `typo3/cms-backend` — affected >=4.2.0 <4.2.13
- Packagist: `typo3/cms-backend` — affected >=4.3.0 <4.3.4
- Packagist: `typo3/cms-backend` — affected >=4.4.0 <4.4.1

## Details
TYPO3 before 4.1.14, 4.2.x before 4.2.13, 4.3.x before 4.3.4 and 4.4.x before 4.4.1 allows SQL Injection on the backend.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3662
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=590719
- https://github.com/TYPO3-CMS/backend
- https://security-tracker.debian.org/tracker/CVE-2010-3662
- https://typo3.org/security/advisory/typo3-sa-2010-012/#SQL_Injection
