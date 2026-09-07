# [H] SQL Injection in LibreNMS

## Summary
Severity: High
Advisory: GHSA-g9xh-3w5g-229r
CVE: CVE-2019-10671
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-g9xh-3w5g-229r
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <1.50.1

## Details
An issue was discovered in LibreNMS through 1.47. It does not parameterize all user supplied input within database queries, resulting in SQL injection. An authenticated attacker can subvert these database queries to extract or manipulate data, as demonstrated by the graph.php sort parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10671
- https://www.darkmatter.ae/xen1thlabs/librenms-multiple-sql-injection-vulnerability-xl-19-025
