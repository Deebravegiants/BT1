# [M] Apache Airflow MySQL Provider is Vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-hhm6-jjf4-6pm3
CVE: CVE-2025-27018
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-hhm6-jjf4-6pm3
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-mysql` — affected >=0 <6.2.0

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Apache Airflow MySQL Provider.

When user triggered a DAG with dump_sql or load_sql functions they could pass a table parameter from a UI, that could cause SQL injection by running SQL that was not intended.
It could lead to data corruption, modification and others.
This issue affects Apache Airflow MySQL Provider: before 6.2.0.

Users are recommended to upgrade to version 6.2.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-27018
- https://github.com/apache/airflow/pull/47254
- https://github.com/apache/airflow/pull/47255
- https://github.com/apache/airflow
- https://lists.apache.org/thread/m8ohgkwz4mq9njohf66sjwqjdy28gvzf
- http://www.openwall.com/lists/oss-security/2025/03/19/4
