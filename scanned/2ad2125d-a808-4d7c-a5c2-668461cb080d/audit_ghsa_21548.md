# [C] OS Command Injection in Apache Airflow

## Summary
Severity: Critical
Advisory: GHSA-7wqf-h36w-47mc
CVE: CVE-2022-38649
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-22
Source: https://github.com/advisories/GHSA-7wqf-h36w-47mc
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <2.3.0

## Details
Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Apache Airflow Pinot Provider, Apache Airflow allows an attacker to control commands executed in the task execution context, without write access to DAG files. This issue affects Apache Airflow Pinot Provider versions prior to 4.0.0. It also impacts any Apache Airflow versions prior to 2.3.0 in case Apache Airflow Pinot Provider is installed (Apache Airflow Pinot Provider 4.0.0 can only be installed for Airflow 2.3.0+). Note that you need to manually install the Pinot Provider version 4.0.0 in order to get rid of the vulnerability on top of Airflow 2.3.0+ version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38649
- https://github.com/apache/airflow/pull/27641
- https://github.com/apache/airflow/commit/1d4fd5c6eacab0b88f8660f9d780174434393f1a
- https://github.com/apache/airflow
- https://lists.apache.org/thread/033o1gbc4ly6dpd2xf1o201v56fbl4dz
