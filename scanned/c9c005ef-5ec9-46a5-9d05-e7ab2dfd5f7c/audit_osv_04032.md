# [M] Apache Airflow: per-DAG RBAC bypass on /ui/partitioned_dag_runs endpoints

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-41014
Aliases: CVE-2026-41014, GHSA-x2x7-p37c-43cr, PYSEC-2026-182
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-airflow-2026-41014
Type: osv

## Affected
- Bitnami: `airflow` — affected >=3.2.0 <3.2.2

## Details
The partitioned_dag_runs endpoints in the Airflow UI enforced only asset-level access control, not per-Dag authorization. An authenticated UI/API user with global Asset:read permission could enumerate partition run state, schedule configuration, and asset wiring for Dags they were not authorized to read. Affects deployments that rely on per-Dag read scoping while granting users broader Asset access. Users are advised to upgrade to `apache-airflow` 3.2.2 or later.

## References
- http://www.openwall.com/lists/oss-security/2026/05/31/4
- https://github.com/apache/airflow/pull/65344
- https://lists.apache.org/thread/12nbzwwby7g883w2j13gn7ny1545xob9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41014
