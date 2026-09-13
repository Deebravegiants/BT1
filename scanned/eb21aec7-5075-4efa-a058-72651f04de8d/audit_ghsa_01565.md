# [C] Insecure default config of Celery worker in Apache Airflow

## Summary
Severity: Critical
Advisory: GHSA-9g2w-5f3v-mfmm
CVE: CVE-2020-11982
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-9g2w-5f3v-mfmm
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.11

## Details
An issue was found in Apache Airflow versions 1.10.10 and below. When using CeleryExecutor, if an attack can connect to the broker (Redis, RabbitMQ) directly, it was possible to insert a malicious payload directly to the broker which could lead to a deserialization attack (and thus remote code execution) on the Worker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11982
- https://github.com/apache/airflow/pull/13612
- https://github.com/apache/airflow/pull/7205
- https://github.com/advisories/GHSA-9g2w-5f3v-mfmm
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-16.yaml
- https://lists.apache.org/thread.html/r7255cf0be3566f23a768e2a04b40fb09e52fcd1872695428ba9afe91%40%3Cusers.airflow.apache.org%3E
