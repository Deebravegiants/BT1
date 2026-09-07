# [M] craftcms/cms vulnerable to cross site scripting in RSS feed widget

## Summary
Severity: Medium
Advisory: GHSA-j4mx-98hw-6rv6
CVE: CVE-2023-31144
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-05
Source: https://github.com/advisories/GHSA-j4mx-98hw-6rv6
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=3.0.0 <3.8.4
- Packagist: `craftcms/cms` — affected >=4.0.0 <4.4.4

## Details
A malformed title in the feed widget of craftcms/cms can deliver an XSS payload. This has been resolved in [this commit](https://github.com/craftcms/cms/commit/52bd161614620edbab2d24d078ca9ebca2528442).

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-j4mx-98hw-6rv6
- https://nvd.nist.gov/vuln/detail/CVE-2023-31144
- https://github.com/craftcms/cms/commit/52bd161614620edbab2d24d078ca9ebca2528442
- https://github.com/craftcms/cms/commit/e2f7e7b7d86a0afa54ce855375d13c7760670764
- https://github.com/craftcms/cms
