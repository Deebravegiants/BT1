# [M] Typo3 XSS Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-h86g-796f-hhfq
CVE: CVE-2011-4632
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-h86g-796f-hhfq
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <4.3.12
- Packagist: `typo3/cms` — affected >=4.4.0 <4.4.9
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.4

## Details
Cross-site Scripting (XSS) in TYPO3 before 4.3.12, 4.4.x before 4.4.9, and 4.5.x before 4.5.4 allows remote attackers to inject arbitrary web script or HTML via the tcemain flash message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4632
- https://github.com/TYPO3/typo3
- https://security-tracker.debian.org/tracker/CVE-2011-4632
- https://typo3.org/security/advisory/typo3-core-sa-2011-001/#XSS
