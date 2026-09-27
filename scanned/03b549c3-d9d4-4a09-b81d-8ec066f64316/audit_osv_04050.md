# [M] Apache Airflow: Cross-team authorization bypass in the asset materialization and dag-run result endpoints

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-68971
Aliases: CVE-2026-68971
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-68971
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow's asset materialization endpoint (`POST /api/v2/assets/{asset_id}/materialize`) and the XCom result check on `wait_dag_run_until_finished` authorized the target Dag without its team, unlike every other authorization site. A team-aware auth manager distinguishes a team-scoped Dag from a global one by that field -- the Keycloak auth manager, for example, checks the `DAG` resource instead of `DAG:<team>` -- so the team-scoped permission that should gate the request was never consulted. In a deployment running multi-team mode with a team-aware auth manager, an authenticated user in one team could trigger Dag runs belonging to another team, supplying their own `dag_run_id` and `conf`, and could read another team's XCom values. Deployments using the FAB auth manager are unaffected, as it has no multi-team support. Users are advised to upgrade to apache-airflow 3.3.1 or later, which resolves the Dag's team at both sites.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/15
- https://github.com/apache/airflow/pull/70893
- https://lists.apache.org/thread/kfxqqwgojdjdnt6bxg3ord4y41y334fo
- https://nvd.nist.gov/vuln/detail/CVE-2026-68971
