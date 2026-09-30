# [H] Apache Airflow allows users with asset materialize permissions to trigger DAGs outside of their permissions

## Summary
Severity: High
Advisory: GHSA-h97w-pm3w-mwmc
CVE: CVE-2026-32228
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-h97w-pm3w-mwmc
Type: github-advisory

## Affected
- PyPI: `apache-airflow-core` — affected >=3.0.0 <3.2.0

## Details
UI / API User with asset materialize permission could trigger dags they had no access to. Users are advised to migrate to Airflow version 3.2.0 that fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-32228
- https://github.com/apache/airflow/pull/63338
- https://github.com/apache/airflow
- https://lists.apache.org/thread/s7c75txgt4qf2rofcn43szfwgcrzy0nj
- http://www.openwall.com/lists/oss-security/2026/04/17/8
