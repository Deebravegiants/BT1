# [M] Apache Airflow: Scheduler remote DoS

## Summary
Severity: Medium
Advisory: BIT-airflow-2023-22888
Aliases: CVE-2023-22888, GHSA-5946-8p38-vffp, PYSEC-2023-105
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2023-22888
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.6.3

## Details
Apache Airflow, versions before 2.6.3, is affected by a vulnerability that allows an attacker to cause a service disruption by manipulating the run_id parameter. This vulnerability is considered low since it requires an authenticated user to exploit it. It is recommended to upgrade to a version that is not affected

## References
- https://github.com/apache/airflow/pull/32293
- https://lists.apache.org/thread/dnlht2hvm7k81k5tgjtsfmk27c76kq7z
- https://nvd.nist.gov/vuln/detail/CVE-2023-22888
