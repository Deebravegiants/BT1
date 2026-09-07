# [M] Apache Superset allows privileged users to conduct error-based SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-gvxg-9hqx-f4rg
CVE: CVE-2026-23980
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-gvxg-9hqx-f4rg
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <6.0.0

## Details
Improper Neutralization of Special Elements used in a SQL Command ('SQL Injection') vulnerability in Apache Superset allows an authenticated user with read access to conduct error-based SQL injection via the sqlExpression or where parameters.

This issue affects Apache Superset: before 6.0.0.

Users are recommended to upgrade to version 6.0.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23980
- https://github.com/apache/superset
- https://lists.apache.org/thread/h4l02zw1pr2vywv0dc5zjn3grdcdhwf4
- http://www.openwall.com/lists/oss-security/2026/02/24/5
