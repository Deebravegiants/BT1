# [M] Apache Airflow `/api/v2/dagReports` executes DAG Python in API

## Summary
Severity: Medium
Advisory: GHSA-273c-4g26-4jpm
CVE: CVE-2025-62402
CWE: CWE-250
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-30
Source: https://github.com/advisories/GHSA-273c-4g26-4jpm
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=3.0.0 <3.1.1

## Details
API users via `/api/v2/dagReports` could perform Dag code execution in the context of the api-server if the api-server was deployed in the environment where Dag files were available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62402
- https://github.com/apache/airflow/pull/56609
- https://github.com/apache/airflow/commit/828aaa0b1d95caf90612a648867c17aec7e87874
- https://github.com/apache/airflow
- https://lists.apache.org/thread/vbzxnxn031wb998hsd7vqnvh4z8nx6rs
- http://www.openwall.com/lists/oss-security/2025/10/29/7
