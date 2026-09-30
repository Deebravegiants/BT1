# [H] Apache Airflow Apache Hive Provider Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-4q2q-q5pw-2342
CVE: CVE-2023-37415
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-13
Source: https://github.com/advisories/GHSA-4q2q-q5pw-2342
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-hive` — affected >=0 <6.1.2

## Details
Improper Input Validation vulnerability in Apache Software Foundation Apache Airflow Apache Hive Provider.

Patching on top of CVE-2023-35797
Before 6.1.2 the proxy_user option can also inject semicolon.

This issue affects Apache Airflow Apache Hive Provider: before 6.1.2.

It is recommended updating provider version to 6.1.2 in order to avoid this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37415
- https://github.com/apache/airflow
- https://lists.apache.org/thread/9wx0jlckbnycjh8nj5qfwxo423zvm41k
- http://www.openwall.com/lists/oss-security/2023/07/12/3
