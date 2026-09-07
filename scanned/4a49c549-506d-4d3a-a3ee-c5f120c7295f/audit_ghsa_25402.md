# [M] Typo3 Backend History Module Vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-2hp4-8h6h-93rr
CVE: CVE-2012-6146
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2hp4-8h6h-93rr
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5 <4.5.21
- Packagist: `typo3/cms` — affected >=4.6 <4.6.14
- Packagist: `typo3/cms` — affected >=4.7 <4.7.6

## Details
The Backend History Module in TYPO3 4.5.x before 4.5.21, 4.6.x before 4.6.14, and 4.7.x before 4.7.6 does not properly restrict access, which allows remote authenticated editors to read the history of arbitrary records via a crafted URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6146
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2012-005
