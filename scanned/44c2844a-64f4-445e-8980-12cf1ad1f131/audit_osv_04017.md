# [H] Apache Airflow: RCE in example DAGs

## Summary
Severity: High
Advisory: BIT-airflow-2022-24288
Aliases: CVE-2022-24288, GHSA-3v7g-4pg3-7r6j, PYSEC-2022-30
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2022-24288
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.2.4

## Details
In Apache Airflow, prior to version 2.2.4, some example DAGs did not properly sanitize user-provided params, making them susceptible to OS Command Injection from the web UI.

## References
- https://lists.apache.org/thread/dbw5ozcmr0h0lhs0yjph7xdc64oht23t
- https://nvd.nist.gov/vuln/detail/CVE-2022-24288
