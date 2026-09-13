# [H] Apache Airflow: Authorization bypass in the Backfill API through conflicting interpretations of the backfill id

## Summary
Severity: High
Advisory: BIT-airflow-2026-68968
Aliases: CVE-2026-68968, PYSEC-2026-3710
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-68968
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow's Backfill API authorized a request against a Dag id supplied by the caller whenever the `backfill_id` path segment failed to parse. The authorization dependency parsed it with `int()` while the route handler parsed it as pydantic's `NonNegativeInt`, which accepts values `int()` rejects (`1.0` coerces to `1`); FastAPI resolves dependencies before endpoint validation, so the two acted on different Dags. An authenticated user holding edit permission on any single Dag could therefore read, pause and cancel backfills belonging to any other Dag, including moving another Dag's queued runs to `failed`. No non-default configuration is required and backfill ids are sequential, so finding a target is trivial. Users are advised to upgrade to apache-airflow 3.3.1 or later, which parses the backfill id with the same type the routes declare.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/12
- https://github.com/apache/airflow/pull/70889
- https://lists.apache.org/thread/f9zmw6xs5b4syhwzbl6fsxm4kf2632ol
- https://nvd.nist.gov/vuln/detail/CVE-2026-68968
