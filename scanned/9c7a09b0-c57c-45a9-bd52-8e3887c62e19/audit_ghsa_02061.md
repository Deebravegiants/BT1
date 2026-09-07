# [H] Cross-Site Request Forgery in forkcms

## Summary
Severity: High
Advisory: GHSA-82xf-8h9p-c6qj
CVE: CVE-2020-23264
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-22
Source: https://github.com/advisories/GHSA-82xf-8h9p-c6qj
Type: github-advisory

## Affected
- Packagist: `forkcms/forkcms` — affected >=0 <5.8.2

## Details
Cross-site request forgery (CSRF) in Fork-CMS before 5.8.2 allow remote attackers to hijack the authentication of logged administrators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23264
- https://github.com/forkcms/forkcms/pull/3123
