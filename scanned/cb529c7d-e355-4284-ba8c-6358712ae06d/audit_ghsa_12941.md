# [H] apache-airflow-providers-apache-drill Improper Input Validation vulnerability

## Summary
Severity: High
Advisory: GHSA-mq4v-6vg4-796c
CVE: CVE-2023-39553
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-11
Source: https://github.com/advisories/GHSA-mq4v-6vg4-796c
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-apache-drill` — affected >=0 <2.4.3

## Details
Improper Input Validation vulnerability in Apache Software Foundation Apache Airflow Drill Provider.

Apache Airflow Drill Provider is affected by a vulnerability that allows an attacker to pass in malicious parameters when establishing a connection with DrillHook giving an opportunity to read files on the Airflow server.
This issue affects Apache Airflow Drill Provider before 2.4.3.
It is recommended to upgrade to a version that is not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39553
- https://github.com/apache/airflow/pull/33074
- https://github.com/apache/airflow/commit/394a727ac2c18d58978bf186a7a92923460ec110
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2023-136.yaml
- https://lists.apache.org/thread/ozpl0opmob49rkcz8svo8wkxyw1395sf
- https://www.openwall.com/lists/oss-security/2023/08/11/1
- http://www.openwall.com/lists/oss-security/2023/08/11/1
