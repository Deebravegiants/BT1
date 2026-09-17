# [M] Improper Privilege Management in apache-airflow

## Summary
Severity: Medium
Advisory: GHSA-4jh2-3c85-q67h
CVE: CVE-2021-45230
CWE: CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-4jh2-3c85-q67h
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.2.0

## Details
In Apache Airflow prior to 2.2.0. This CVE applies to a specific case where a User who has "can_create" permissions on DAG Runs can create Dag Runs for dags that they don't have "edit" permissions for.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45230
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2022-11.yaml
- https://lists.apache.org/thread/m778ojn0k595rwco4ht9wjql89mjoxnl
