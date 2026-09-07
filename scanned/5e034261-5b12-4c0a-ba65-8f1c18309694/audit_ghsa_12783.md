# [H] Apache Superset vulnerable to Cross-Site Request Forgery via legacy REST API endpoints

## Summary
Severity: High
Advisory: GHSA-7222-r37x-8q3m
CVE: CVE-2022-43719
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-16
Source: https://github.com/advisories/GHSA-7222-r37x-8q3m
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0
- PyPI: `apache-superset` — affected 2.0.0

## Details
Two legacy REST API endpoints for approval and request access are vulnerable to cross site request forgery. This issue affects Apache Superset version 1.5.2 and prior versions and version 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43719
- https://github.com/apache/superset
- https://lists.apache.org/thread/xc309h2dphrkg33154djf3nqlh2xc1c0
