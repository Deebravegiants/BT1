# [C] Code Injection in SEOmatic

## Summary
Severity: Critical
Advisory: GHSA-g7xr-v82w-qggq
CVE: CVE-2021-41749
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-13
Source: https://github.com/advisories/GHSA-g7xr-v82w-qggq
Type: github-advisory

## Affected
- Packagist: `nystudio107/craft-seomatic` — affected >=0 <3.4.11

## Details
In the SEOmatic plugin up to 3.4.11 for Craft CMS 3, it is possible for unauthenticated attackers to perform a Server-Side Template Injection, allowing for remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41749
- https://github.com/nystudio107/craft-seomatic/commit/3fee7d50147cdf3f999cfc1e04cbc3fb3d9f2f7d
- https://github.com/nystudio107/craft-seomatic
- https://github.com/nystudio107/craft-seomatic/blob/develop/CHANGELOG.md
