# [M] Apache Airflow: /ui/dependencies scheduling graph leaks unreadable Dag identifiers via trigger/sensor dep.source/dep.target

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-48891
Aliases: CVE-2026-48891, GHSA-3322-mjxh-9mp5, PYSEC-2026-2086
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-airflow-2026-48891
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.0

## Details
A bug in Apache Airflow's `/ui/dependencies` scheduling graph endpoint applied the caller's readable-Dag filter to the top-level serialized Dag key but still emitted referenced Dag IDs through the `dep.source` and `dep.target` fields of trigger / sensor dependency entries. An authenticated UI user with read permission on some Dags could enumerate the identifiers of other Dags they were not authorized to read by inspecting the dependency graph for trigger / sensor references. Affects deployments that rely on per-Dag read scoping to keep Dag identifiers private across teams. This is a residual gap in the fix for CVE-2026-28563, which filtered the top-level Dag key but did not propagate the filter into the trigger / sensor dep-source / dep-target fields. Users who already upgraded for CVE-2026-28563 should additionally upgrade to `apache-airflow` 3.3.0 or later to cover the residual trigger / sensor dependency leak.

## References
- https://github.com/apache/airflow/pull/67627
- https://lists.apache.org/thread/wzc8nflg94rq6w8f5tvtlo0o3g4wjrfl
- https://nvd.nist.gov/vuln/detail/CVE-2026-48891
- https://www.cve.org/CVERecord?id=CVE-2026-28563
