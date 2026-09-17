# [M] Apache Airflow exposes SQL stack trace despite "api/expose_stack_traces" set to false

## Summary
Severity: Medium
Advisory: GHSA-w7cf-2pmc-5m4c
CVE: CVE-2026-30912
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-18
Source: https://github.com/advisories/GHSA-w7cf-2pmc-5m4c
Type: github-advisory

## Affected
- PyPI: `apache-airflow-core` — affected >=0 <3.2.0

## Details
In case of SQL errors, exception/stack trace of errors was exposed in API even if "api/expose_stack_traces" was set to false. That could lead to exposing additional information to potential attacker. Users are recommended to upgrade to Apache Airflow 3.2.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30912
- https://github.com/apache/airflow/pull/63028
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2026-18.yaml
- https://lists.apache.org/thread/tp6kz1hnfb3zsrrtg19myo8x5x80w8r9
- http://www.openwall.com/lists/oss-security/2026/04/17/5
