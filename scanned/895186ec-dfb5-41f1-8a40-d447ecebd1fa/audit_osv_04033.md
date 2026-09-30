# [H] Apache Airflow: API authorization bypass: bulk TaskInstances allows cross-DAG mutation

## Summary
Severity: High
Advisory: BIT-airflow-2026-41084
Aliases: CVE-2026-41084, GHSA-mxq5-f9c5-w4p5, PYSEC-2026-183
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-airflow-2026-41084
Type: osv

## Affected
- Bitnami: `airflow` — affected >=3.2.0 <3.2.2

## Details
A bug in Apache Airflow's bulk Task Instances API (`PATCH/DELETE /api/v2/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances`) evaluated authorization against the `dag_id` resolved from the URL path while operating on the `dag_id` / `dag_run_id` extracted from request-body entity fields. An authenticated UI/API user with edit permission on one Dag could mutate Task Instance state in any other Dag by keeping the authorized Dag's ID in the URL path and naming the target Dag's IDs in the request body entities. Affects deployments that rely on per-Dag edit-scope to keep Task Instance state isolated between teams. Users are advised to upgrade to `apache-airflow` 3.2.2 or later.

## References
- http://www.openwall.com/lists/oss-security/2026/05/31/7
- https://github.com/apache/airflow/pull/64288
- https://lists.apache.org/thread/w0hdcqfr71hf9rl1bwvpjs7q9yp1bldk
- https://nvd.nist.gov/vuln/detail/CVE-2026-41084
