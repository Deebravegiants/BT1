# [H] Apache Airflow Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-3h4m-m55v-gx4m
CVE: CVE-2023-36543
CWE: CWE-1333, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-3h4m-m55v-gx4m
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.6.3

## Details
Apache Airflow, versions before 2.6.3, has a vulnerability where an authenticated user can use crafted input to make the current request hang. It is recommended to upgrade to a version that is not affected

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-36543
- https://github.com/apache/airflow/pull/32060
- https://github.com/apache/airflow/commit/116e607ddcb32480e57c342f48226545ac6fc315
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-106.yaml
- https://lists.apache.org/thread/tokfs980504ylgk3cv3hjlnrtbv4tng4
