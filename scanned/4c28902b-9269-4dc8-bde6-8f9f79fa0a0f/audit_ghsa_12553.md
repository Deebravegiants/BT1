# [H] Apache Airflow JDBC Provider Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-mm87-c3x2-6f89
CVE: CVE-2023-22886
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-29
Source: https://github.com/advisories/GHSA-mm87-c3x2-6f89
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-jdbc` — affected >=0 <4.0.0

## Details
Improper Input Validation vulnerability in Apache Software Foundation Apache Airflow JDBC Provider. Airflow JDBC Provider Connection’s [Connection URL] parameters had no restrictions, which made it possible to implement RCE attacks via different type JDBC drivers, obtain airflow server permission. This issue affects Apache Airflow JDBC Provider: before 4.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22886
- https://github.com/apache/airflow
- https://lists.apache.org/thread/ynbjwp4n0vzql0xzhog1gkp1ovncf8j3
