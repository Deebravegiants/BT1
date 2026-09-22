# [M] Apache Airflow: Connections test API: team-scope guard bypass resolves another team's environment Connection

## Summary
Severity: Medium
Advisory: BIT-airflow-2026-68076
Aliases: CVE-2026-68076, PYSEC-2026-3709
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-airflow-2026-68076
Type: osv

## Affected
- Bitnami: `airflow` — affected >=0 <3.3.1

## Details
Apache Airflow's environment-variable secrets backend resolved a team-scoped Connection or Variable from the wrong team's scope. The guard meant to prevent this only ran when no team scope was supplied, and its pattern could not match a team name containing an underscore, which team names are allowed to contain. When the guard did not apply, the lookup fell through to an unconditional global read that resolved the stored `AIRFLOW_CONN__<TEAM>___<ID>` variable regardless of which team asked. In multi-team mode an authenticated user of one team could therefore have `POST /api/v2/connections/test` resolve another team's Connection and authenticate outward with that team's credentials; the endpoint uses the credentials rather than returning them. Exploitation requires `[core] multi_team` enabled, `[core] test_connection` set to `Enabled` (it ships `Disabled`), team-scoped secrets provisioned as environment variables in the API-server process, and knowledge of the encoded identifier. Redirecting the test at an attacker-controlled host is separately blocked. Users are advised to upgrade to apache-airflow 3.3.1 or later.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/11
- https://github.com/apache/airflow/pull/70736
- https://github.com/apache/airflow/pull/70902
- https://lists.apache.org/thread/v4mc51dgmrc1t82mhzsngsgzo2gxsf2l
- https://nvd.nist.gov/vuln/detail/CVE-2026-68076
