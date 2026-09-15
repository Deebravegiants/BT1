# [C] Command Injection in Apache Airflow and Apache Airflow MySQL Provider

## Summary
Severity: Critical
Advisory: GHSA-c732-xvv8-g94c
CVE: CVE-2023-22884
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-21
Source: https://github.com/advisories/GHSA-c732-xvv8-g94c
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.5.1
- PyPI: `apache-airflow-providers-mysql` — affected >=0 <4.0.0

## Details
Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in Apache Software Foundation Apache Airflow, Apache Software Foundation Apache Airflow MySQL Provider.This issue affects Apache Airflow: before 2.5.1; Apache Airflow MySQL Provider: before 4.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22884
- https://github.com/apache/airflow/pull/28811
- https://github.com/apache/airflow
- https://lists.apache.org/thread/0l0j3nt0t7fzrcjl2ch0jgj6c58kxs5h
