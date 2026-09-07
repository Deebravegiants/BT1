# [H] Apache Airflow Common SQL Provider Vulnerable to SQL Injection

## Summary
Severity: High
Advisory: GHSA-5r62-mjf5-xwhj
CVE: CVE-2025-30473
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-5r62-mjf5-xwhj
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-common-sql` — affected >=0 <1.24.1

## Details
Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection') vulnerability in Apache Airflow Common SQL Provider.

When using the partition clause in SQLTableCheckOperator as parameter (which was a recommended pattern), Authenticated UI User could inject arbitrary SQL command when triggering DAG exposing partition_clause to the user.
This allowed the DAG Triggering user to escalate privileges to execute those arbitrary commands which they normally would not have.


This issue affects Apache Airflow Common SQL Provider: before 1.24.1.

Users are recommended to upgrade to version 1.24.1, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30473
- https://github.com/apache/airflow/pull/48098
- https://github.com/apache/airflow
- https://lists.apache.org/thread/53klkv790cylqcop0350w7nfq1y6h0t2
- http://www.openwall.com/lists/oss-security/2025/04/04/2
- http://www.openwall.com/lists/oss-security/2025/04/06/1
- http://www.openwall.com/lists/oss-security/2025/04/06/2
- http://www.openwall.com/lists/oss-security/2025/04/06/3
