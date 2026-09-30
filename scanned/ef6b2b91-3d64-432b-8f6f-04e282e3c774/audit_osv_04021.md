# [M] Apache Airflow Spark Provider RCE that bypass restrictions to read arbitrary files

## Summary
Severity: Medium
Advisory: BIT-airflow-2022-40954
Aliases: CVE-2022-40954, GHSA-45r6-j3cc-6mxx, PYSEC-2026-770
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2022-40954
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.3.0

## Details
Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Apache Airflow Spark Provider, Apache Airflow allows an attacker to read arbtrary files in the task execution context, without write access to DAG files. This issue affects Spark Provider versions prior to 4.0.0. It also impacts any Apache Airflow versions prior to 2.3.0 in case Spark Provider is installed (Spark Provider 4.0.0 can only be installed for Airflow 2.3.0+). Note that you need to manually install the Spark Provider version 4.0.0 in order to get rid of the vulnerability on top of Airflow 2.3.0+ version that has lower version of the Spark Provider installed).

## References
- https://github.com/apache/airflow/pull/27646
- https://lists.apache.org/thread/0tmdlnmjs5t4gsx5fy73tb6zd3jztq45
- https://nvd.nist.gov/vuln/detail/CVE-2022-40954
