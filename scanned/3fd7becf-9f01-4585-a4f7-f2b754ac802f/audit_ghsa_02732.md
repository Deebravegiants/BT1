# [M] Incorrect Authorization in TYPO3 extension

## Summary
Severity: Medium
Advisory: GHSA-cv9j-78f7-w6v9
CVE: CVE-2020-25025
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-cv9j-78f7-w6v9
Type: github-advisory

## Affected
- Packagist: `localizationteam/l10nmgr` — affected >=0 <7.4.0
- Packagist: `localizationteam/l10nmgr` — affected >=8.0.0 <8.7.0
- Packagist: `localizationteam/l10nmgr` — affected >=9.0.0 <9.2.0

## Details
The l10nmgr (aka Localization Manager) extension before 7.4.0, 8.x before 8.7.0, and 9.x before 9.2.0 for TYPO3 allows Information Disclosure (translatable fields).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25025
- https://typo3.org/help/security-advisories
- https://typo3.org/security/advisory/typo3-ext-sa-2020-016
