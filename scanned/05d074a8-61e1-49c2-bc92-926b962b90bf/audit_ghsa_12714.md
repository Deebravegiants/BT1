# [M] Apache Airflow ODBC Provider, Apache Airflow MSSQL Provider Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q57w-826p-46jr
CVE: CVE-2023-35798
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-27
Source: https://github.com/advisories/GHSA-q57w-826p-46jr
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-odbc` — affected >=0 <4.0.0
- PyPI: `apache-airflow-providers-microsoft-mssql` — affected >=0 <3.4.1

## Details
Input Validation vulnerability in Apache Software Foundation Apache Airflow ODBC Provider, Apache Software Foundation Apache Airflow MSSQL Provider.This vulnerability is considered low since it requires DAG code to use `get_sqlalchemy_connection` and someone with access to connection resources specifically updating the connection to exploit it.

This issue affects Apache Airflow ODBC Provider: before 4.0.0; Apache Airflow MSSQL Provider: before 3.4.1.

It is recommended to upgrade to a version that is not affected

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35798
- https://github.com/apache/airflow/pull/31984
- https://github.com/apache/airflow/commit/b6836986846058e9e5fa271fb7b22ae721020787
- https://github.com/apache/airflow
- https://lists.apache.org/thread/951rb9m7wwox5p30tdvcfjxq8j1mp4pj
