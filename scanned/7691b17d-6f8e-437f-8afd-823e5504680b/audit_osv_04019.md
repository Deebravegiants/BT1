# [C] Apache Airlfow Pig Provider RCE

## Summary
Severity: Critical
Advisory: BIT-airflow-2022-40189
Aliases: CVE-2022-40189, GHSA-rmf2-pwfq-h75j, PYSEC-2026-270
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2022-40189
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.3.0

## Details
Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in Apache Airflow Pig Provider, Apache Airflow allows an attacker to control commands executed in the task execution context, without write access to DAG files. This issue affects Pig Provider versions prior to 4.0.0. It also impacts any Apache Airflow versions prior to 2.3.0 in case Pig Provider is installed (Pig Provider 4.0.0 can only be installed for Airflow 2.3.0+). Note that you need to manually install the Pig Provider version 4.0.0 in order to get rid of the vulnerability on top of Airflow 2.3.0+ version.

## References
- https://github.com/apache/airflow/pull/27644
- https://lists.apache.org/thread/yxnfzfw2w9pj5s785k3rlyly4y44sd15
- https://nvd.nist.gov/vuln/detail/CVE-2022-40189
