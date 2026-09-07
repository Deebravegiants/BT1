# [M] TYPO3 is vulnerable to Information Disclosure in the HTML mailing API

## Summary
Severity: Medium
Advisory: GHSA-5f2f-hr23-j59j
CVE: CVE-2010-3673
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-04-21
Source: https://github.com/advisories/GHSA-5f2f-hr23-j59j
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=0 <4.2.13
- Packagist: `typo3/cms-core` — affected >=4.3 <4.3.4
- Packagist: `typo3/cms-core` — affected >=4.4 <4.4.1

## Details
TYPO3 before 4.2.13, 4.3.x before 4.3.4 and 4.4.x before 4.4.1 allows information disclosure in the mail header of the HTML mailing API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-3673
- https://github.com/TYPO3/typo3/commit/3e24a0fff04897826a12e5cac16b5b0a3848cf2d
- https://github.com/TYPO3/typo3/commit/46693d4930d0bce64c5bdd4274224724041cef2f
- https://github.com/TYPO3/typo3/commit/a3a62d99507a9e686274306df0cc1c31f4394981
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=590719
- https://github.com/TYPO3-CMS/core
- https://security-tracker.debian.org/tracker/CVE-2010-3673
- https://typo3.org/security/advisory/typo3-sa-2010-012/#Information_Disclosure
