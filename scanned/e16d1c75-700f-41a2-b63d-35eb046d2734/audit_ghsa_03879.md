# [C] SQL Injection in usmanhalalit/pixie

## Summary
Severity: Critical
Advisory: GHSA-68wg-qv6r-j4vp
CVE: CVE-2019-10766
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-20
Source: https://github.com/advisories/GHSA-68wg-qv6r-j4vp
Type: github-advisory

## Affected
- Packagist: `usmanhalalit/pixie` — affected >=0 <1.0.3
- Packagist: `usmanhalalit/pixie` — affected >=2.0.0 <2.0.2

## Details
Pixie versions 1.0.x before 1.0.3, and 2.0.x before 2.0.2 allow SQL Injection in the limit() function due to improper sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10766
- https://github.com/usmanhalalit/pixie/commit/9bd991021abbcbfb19347a07dca8b7e518b8abc9
- https://snyk.io/vuln/SNYK-PHP-USMANHALALITPIXIE-534879
