# [M] Cross-site scripting in media2click

## Summary
Severity: Medium
Advisory: GHSA-xpxm-pf7g-2534
CVE: CVE-2021-31778
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-xpxm-pf7g-2534
Type: github-advisory

## Affected
- Packagist: `amazing/media2click` — affected >=1.0.0 <1.3.3

## Details
The media2click (aka 2 Clicks for External Media) extension 1.x before 1.3.3 for TYPO3 allows XSS by a backend user account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31778
- https://github.com/ghermens/media2click/commit/3c4e413fbc7d35c47212e754c24d5070637a11a3
- https://packagist.org/packages/amazing/media2click
- https://typo3.org/security/advisory/typo3-ext-sa-2021-004
