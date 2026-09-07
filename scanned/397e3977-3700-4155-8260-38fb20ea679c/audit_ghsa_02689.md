# [M] Cross-site Request Forgery (CSRF) in joplin

## Summary
Severity: Medium
Advisory: GHSA-gjwp-7v3g-99pj
CVE: CVE-2021-23431
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-gjwp-7v3g-99pj
Type: github-advisory

## Affected
- npm: `joplin` — affected >=0 <2.3.2

## Details
The package joplin before 2.3.2 are vulnerable to Cross-site Request Forgery (CSRF) due to missing CSRF checks in various forms.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23431
- https://github.com/laurent22/joplin/commit/19b45de2981c09f6f387498ef96d32b4811eba5e
- https://github.com/laurent22/joplin
- https://snyk.io/vuln/SNYK-JS-JOPLIN-1325537
