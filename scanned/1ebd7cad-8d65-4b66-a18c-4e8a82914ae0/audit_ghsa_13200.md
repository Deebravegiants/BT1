# [M] Apache Superset vulnerable to improper data authorization

## Summary
Severity: Medium
Advisory: GHSA-v594-2c97-hx38
CVE: CVE-2023-27523
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-v594-2c97-hx38
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0

## Details
Improper data authorization check on Jinja templated queries in Apache Superset up to and including 2.1.0 allows for an authenticated user to issue queries on database tables they may not have access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27523
- https://github.com/apache/superset
- https://lists.apache.org/thread/3y97nmwm956b6zg3l8dh9oj0w7dj945h
