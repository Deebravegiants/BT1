# [H] Apache Airflow Drill Provider vulnerable to improper input validation 

## Summary
Severity: High
Advisory: GHSA-85pf-r4c7-3j9r
CVE: CVE-2023-28707
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-04-07
Source: https://github.com/advisories/GHSA-85pf-r4c7-3j9r
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-drill` — affected >=0 <2.3.2

## Details
Apache Software Foundation's Apache Airflow Drill Provider before 2.3.2 is vulnerable to improper input validation because the host passed in drill connection is not sanitized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28707
- https://github.com/apache/airflow/pull/30215
- https://github.com/apache/airflow/commit/63d9b24aad0b4b9397682ddac1ea5824354789b3
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-3.yaml
- https://lists.apache.org/thread/dfoj7q1nd0vhhsl8fjg63z4j6mfmdxtk
- https://www.openwall.com/lists/oss-security/2023/04/07/1
- http://www.openwall.com/lists/oss-security/2023/04/07/1
