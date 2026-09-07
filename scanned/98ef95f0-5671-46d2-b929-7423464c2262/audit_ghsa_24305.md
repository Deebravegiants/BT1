# [M] Aimeos Typo3 extension contains Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-73wv-rgj7-vjj9
CVE: CVE-2021-28380
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-73wv-rgj7-vjj9
Type: github-advisory

## Affected
- Packagist: `aimeos/aimeos-typo3` — affected >=0 <19.10.12
- Packagist: `aimeos/aimeos-typo3` — affected >=20.0.0 <20.10.5

## Details
The aimeos (aka Aimeos shop and e-commerce framework) extension before 19.10.12 and 20.x before 20.10.5 for TYPO3 allows Cross-site Scripting (XSS) via a backend user account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28380
- https://typo3.org/security/advisory/typo3-ext-sa-2021-003
