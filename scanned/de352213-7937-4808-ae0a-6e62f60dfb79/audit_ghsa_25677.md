# [M] Typo3 Arbitrary File Delete

## Summary
Severity: Medium
Advisory: GHSA-9vxq-mxw5-mcgp
CVE: CVE-2011-4902
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-9vxq-mxw5-mcgp
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=0 <4.3.12
- Packagist: `typo3/cms` — affected >=4.4.0 <4.4.9
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.4

## Details
TYPO3 before 4.3.12, 4.4.x before 4.4.9, and 4.5.x before 4.5.4 allows remote attackers to delete arbitrary files on the webserver.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4902
- https://github.com/TYPO3/typo3
- https://security-tracker.debian.org/tracker/CVE-2011-4902
- https://typo3.org/security/advisory/typo3-core-sa-2011-001/#Unserialize
