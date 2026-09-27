# [C] Command injection via Celery broker in Apache Airflow

## Summary
Severity: Critical
Advisory: GHSA-976r-qfjj-c24w
CVE: CVE-2020-11981
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-976r-qfjj-c24w
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.11rc1

## Details
An issue was found in Apache Airflow versions 1.10.10 and below. When using CeleryExecutor, if an attacker can connect to the broker (Redis, RabbitMQ) directly, it is possible to inject commands, resulting in the celery worker running arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11981
- https://github.com/apache/airflow/commit/1dda6fdde7c6bcaf0d6534786beeeba868006dd2
- https://github.com/apache/airflow/commit/afa4b11fddfdbadb048f742cf66d5c21c675a5c8
- https://github.com/advisories/GHSA-976r-qfjj-c24w
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-15.yaml
- https://lists.apache.org/thread.html/r7255cf0be3566f23a768e2a04b40fb09e52fcd1872695428ba9afe91%40%3Cusers.airflow.apache.org%3E
- https://web.archive.org/web/20220427031325/https://issues.apache.org/jira/browse/AIRFLOW-6351
