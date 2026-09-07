# [M] Erxes Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2977-5php-6789
CVE: CVE-2024-57189
CWE: CWE-22, CWE-24
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-06-10
Source: https://github.com/advisories/GHSA-2977-5php-6789
Type: github-advisory

## Affected
- npm: `erxes` — affected >=0 <1.6.2

## Details
In Erxes <1.6.2, an authenticated attacker can write to arbitrary files on the system using a Path Traversal vulnerability in the importHistoriesCreate GraphQL mutation handler.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57189
- https://github.com/erxes/erxes/commit/d626070a0fcd435ae29e689aca051ccfb440c2f3
- https://github.com/erxes/erxes
- https://www.sonarsource.com/blog/micro-services-major-headaches-detecting-vulnerabilities-in-erxes-microservices
