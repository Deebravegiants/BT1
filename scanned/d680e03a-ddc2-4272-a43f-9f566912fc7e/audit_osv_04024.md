# [M] Apache Airflow: Access to DAGs without relevant permission

## Summary
Severity: Medium
Advisory: BIT-airflow-2023-35908
Aliases: CVE-2023-35908, GHSA-2h84-3crq-vgfj, PYSEC-2023-119
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2023-35908
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.6.3

## Details
Apache Airflow, versions before 2.6.3, is affected by a vulnerability that allows unauthorized read access to a DAG through the URL. It is recommended to upgrade to a version that is not affected

## References
- https://github.com/apache/airflow/pull/32014
- https://lists.apache.org/thread/vsflptk5dt30vrfggn96nx87d7zr6yvw
- https://nvd.nist.gov/vuln/detail/CVE-2023-35908
