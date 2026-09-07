# [C] Typo3 Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-79gv-5cgx-x6rx
CVE: CVE-2011-4628
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-79gv-5cgx-x6rx
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <4.3.12
- Packagist: `typo3/cms` — affected >=4.4.0 <4.4.9
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.4

## Details
TYPO3 before 4.3.12, 4.4.x before 4.4.9, and 4.5.x before 4.5.4 allows remote attackers to bypass authentication mechanisms in the backend through a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4628
- https://github.com/TYPO3/typo3
- https://security-tracker.debian.org/tracker/CVE-2011-4628
- https://typo3.org/security/advisory/typo3-core-sa-2011-001/#Authentication_Delay_Bypass
