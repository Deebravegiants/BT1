# [M] Apache Airflow: Bypass permission verification to view task instances of other dags

## Summary
Severity: Medium
Advisory: BIT-airflow-2023-42663
Aliases: CVE-2023-42663, GHSA-32wr-qqw6-5mfp, PYSEC-2023-197
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-airflow-2023-42663
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <2.7.2

## Details
Apache Airflow, versions before 2.7.2, has a vulnerability that allows an authorized user who has access to read specific DAGs only, to read information about task instances in other DAGs.
Users of Apache Airflow are advised to upgrade to version 2.7.2 or newer to mitigate the risk associated with this vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2023/11/12/2
- https://github.com/apache/airflow/pull/34315
- https://lists.apache.org/thread/xj86cvfkxgd0cyqfmz6mh1bsfc61c6o9
- https://nvd.nist.gov/vuln/detail/CVE-2023-42663
