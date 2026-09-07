# [C] sr_freecap for Typo3 RCE Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-598p-rv6p-g7qc
CVE: CVE-2019-16699
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-598p-rv6p-g7qc
Type: github-advisory

## Affected
- Packagist: `sjbr/sr-freecap` — affected >=2.5.0 <2.5.3
- Packagist: `sjbr/sr-freecap` — affected >=0 <2.4.6

## Details
The sr_freecap (aka freeCap CAPTCHA) extension 2.4.5 and below and 2.5.2 and below for TYPO3 fails to sanitize user input, which allows execution of arbitrary Extbase actions, resulting in Remote Code Execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16699
- https://extensions.typo3.org/extension/sr_freecap
- https://github.com/mavolkmer/sr-freecap
- https://typo3.org/security/advisory/typo3-ext-sa-2019-018
