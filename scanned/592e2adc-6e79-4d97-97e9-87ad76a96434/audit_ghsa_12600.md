# [H] Apache Airflow ODBC Provider Argument Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-9766-v29c-4vm7
CVE: CVE-2023-34395
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-27
Source: https://github.com/advisories/GHSA-9766-v29c-4vm7
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-odbc` — affected >=0 <4.0.0

## Details
Improper Neutralization of Argument Delimiters in a Command ('Argument Injection') vulnerability in Apache Software Foundation Apache Airflow ODBC Provider.
In OdbcHook, A privilege escalation vulnerability exists in a system due to controllable ODBC driver parameters that allow the loading of arbitrary dynamic-link libraries, resulting in command execution.
Starting version 4.0.0 driver can be set only from the hook constructor.
This issue affects Apache Airflow ODBC Provider: before 4.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-34395
- https://github.com/apache/airflow/pull/31713
- https://github.com/apache/airflow/commit/2844dad1c762f5c7dd1271866d3661bf66657300
- https://github.com/apache/airflow
- https://lists.apache.org/thread/l26yykftzbhc9tgcph8cso88bc2lqwwd
