# [H] Apache Airflow may allow authenticated users who have been deactivated to continue using the UI or API

## Summary
Severity: High
Advisory: GHSA-3q8r-f3pj-3gc4
CVE: CVE-2022-41672
CWE: CWE-285, CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-3q8r-f3pj-3gc4
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.4.1rc1

## Details
In Apache Airflow, prior to version 2.4.1, deactivating a user wouldn't prevent an already authenticated user from being able to continue using the UI or API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41672
- https://github.com/apache/airflow/pull/26635
- https://github.com/apache/airflow/commit/12bfb571a895a28a58d3189b0fc10cfc1b89e24c
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2022-42983.yaml
- https://lists.apache.org/thread/ohf3pvd3dftb8zb01yngbn1jtkq5m08y
