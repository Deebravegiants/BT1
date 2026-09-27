# [M] Apache Superset's SQL Alchemy connector vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-cxvp-3frm-3876
CVE: CVE-2022-41703
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-16
Source: https://github.com/advisories/GHSA-cxvp-3frm-3876
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0
- PyPI: `apache-superset` — affected 2.0.0

## Details
A vulnerability in the SQL Alchemy connector of Apache Superset allows an authenticated user with read access to a specific database to add subqueries to the WHERE and HAVING fields referencing tables on the same database that the user should not have access to, despite the user having the feature flag "ALLOW_ADHOC_SUBQUERY" disabled (default value). This issue affects Apache Superset version 1.5.2 and prior versions and version 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41703
- https://github.com/apache/superset
- https://lists.apache.org/thread/g7jjw0okxjk5y57pbbxy19ydw42kqcos
