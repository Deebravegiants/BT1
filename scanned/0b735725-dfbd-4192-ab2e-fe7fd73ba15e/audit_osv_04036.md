# [M] Apache Airflow: Event Log detail endpoint bypasses DAG-scoped event log permission filter

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-46764
Aliases: CVE-2026-46764, GHSA-qphr-3mvq-v466, PYSEC-2026-2354
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-airflow-2026-46764
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.2.2

## Details
The Event Log detail endpoint `GET /api/v2/eventLogs/{event_log_id}` in Apache Airflow fetched audit-log rows directly by numeric ID after only the generic Audit Log permission check, while the collection endpoint `GET /api/v2/eventLogs` applied per-Dag scoping. An authenticated UI/API user with audit-log read permission for one Dag could retrieve audit-log entries for any other Dag by guessing or enumerating the numeric event log ID. Affects deployments that rely on per-Dag audit-log scoping. Users are advised to upgrade to `apache-airflow` 3.2.2 or later.

## References
- http://www.openwall.com/lists/oss-security/2026/05/31/14
- https://github.com/apache/airflow/pull/67112
- https://lists.apache.org/thread/ctrbj7q3m86g4qxmo9ponojgmzrcoqpv
- https://nvd.nist.gov/vuln/detail/CVE-2026-46764
