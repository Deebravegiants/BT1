# [M] Typo3 XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3w22-wrwx-2r75
CVE: CVE-2018-6905
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3w22-wrwx-2r75
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <9.2.0

## Details
The page module in TYPO3 before 8.7.11 has XSS via `$GLOBALS['TYPO3_CONF_VARS']['SYS']['sitename']`, as demonstrated by an admin entering a crafted site name during the installation process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6905
- https://github.com/TYPO3/typo3/commit/d2c0ea7db3b31a796a82f9d39f77f9983beb7c35
- https://forge.typo3.org/issues/84191
- https://github.com/pradeepjairamani/TYPO3-XSS-POC
- http://www.securitytracker.com/id/1040755
