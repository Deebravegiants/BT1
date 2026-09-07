# [M] Apache Airflow: XSS vulnerability in Task Instance Log/Log Details

## Summary
Severity: Medium
Advisory: GHSA-52gm-qmg3-r4qp
CVE: CVE-2024-32077
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-52gm-qmg3-r4qp
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=2.9.0 <2.9.1

## Details
Apache Airflow version 2.9.0 has a vulnerability that allows an authenticated attacker to inject malicious data into the task instance logs. 
Users are recommended to upgrade to version 2.9.1, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-32077
- https://github.com/apache/airflow/pull/38882
- https://github.com/apache/airflow/commit/87acf61f574daf47ce9e03a986e352a2c727f4ce
- https://github.com/apache/airflow
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-airflow/PYSEC-2024-264.yaml
- https://lists.apache.org/thread/gsjmnrqb3m5fzp0vgpty1jxcywo91v77
- http://www.openwall.com/lists/oss-security/2024/05/14/1
