# [M] Apache Superset: Incomplete DISALLOWED_SQL_FUNCTIONS default list for ClickHouse engine

## Summary
Severity: Medium
Advisory: GHSA-48m2-v2r8-h23m
CVE: CVE-2026-23969
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-48m2-v2r8-h23m
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <4.1.2

## Details
Apache Superset utilizes a configurable dictionary, DISALLOWED_SQL_FUNCTIONS, to restrict the execution of potentially sensitive SQL functions within SQL Lab and charts. While this feature included restrictions for engines like PostgreSQL, a vulnerability was reported where the default list for the ClickHouse engine was incomplete.

This issue affects Apache Superset: before 4.1.2.

Users are recommended to upgrade to version 4.1.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-23969
- https://github.com/apache/superset
- https://lists.apache.org/thread/2q22sp4oj3krcgdkxchhtht0vgwp2wnd
- http://www.openwall.com/lists/oss-security/2026/02/24/4
