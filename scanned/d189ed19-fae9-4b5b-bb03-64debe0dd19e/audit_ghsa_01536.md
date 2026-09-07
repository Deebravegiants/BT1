# [M] Multiple stored XSS in RBAC Admin screens in Apache Airflow

## Summary
Severity: Medium
Advisory: GHSA-q4p3-qw5c-mhpc
CVE: CVE-2020-11983
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-q4p3-qw5c-mhpc
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <1.10.11

## Details
An issue was found in Apache Airflow versions 1.10.10 and below. It was discovered that many of the admin management screens in the new/RBAC UI handled escaping incorrectly, allowing authenticated users with appropriate permissions to create stored XSS attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11983
- https://github.com/advisories/GHSA-q4p3-qw5c-mhpc
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2020-17.yaml
- https://lists.apache.org/thread.html/r7255cf0be3566f23a768e2a04b40fb09e52fcd1872695428ba9afe91%40%3Cusers.airflow.apache.org%3E
