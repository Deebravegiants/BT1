# [M] ThinkPHP Cross-Site Scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-969f-v7jv-pgj3
CVE: CVE-2024-34467
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-04
Source: https://github.com/advisories/GHSA-969f-v7jv-pgj3
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected >=8.0.0 <8.0.4
- Packagist: `topthink/framework` — affected >=6.1.0 <6.1.5
- Packagist: `topthink/framework` — affected >=0 <6.0.17

## Details
ThinkPHP 8.0.3 allows remote attackers to exploit XSS due to inadequate filtering of function argument values in think_exception.tpl.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34467
- https://github.com/top-think/framework/issues/2996
- https://github.com/top-think/framework/commit/403358cd3e510e2fdab63f951930bdd093314eee
- https://github.com/top-think/framework/commit/57d1950a1844ef8d3098ea290032aeb92e2e32c3
- https://github.com/top-think/framework/commit/d3904e51e279c3b72ee206192aeccf9b1cffb534
- https://github.com/top-think/framework
