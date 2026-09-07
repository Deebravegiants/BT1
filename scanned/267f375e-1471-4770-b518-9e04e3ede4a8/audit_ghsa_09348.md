# [M] Apache Airflow Amazon provider: Prevent unauthorized access to team-scoped secrets in AWS Secrets Manager and SSM Parameter Store backends

## Summary
Severity: Medium
Advisory: GHSA-g9qc-qf28-hhqx
CVE: CVE-2026-42526
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-g9qc-qf28-hhqx
Type: github-advisory

## Affected
- PyPI: `apache-airflow-providers-amazon` — affected >=0 <9.28.0

## Details
In the AWS Secrets Manager and SSM Parameter Store secrets backends of `apache-airflow-providers-amazon` prior to 9.28.0, the team-scoping logic could resolve a `conn_id` containing a `/` (e.g. `"my_team/conn"`) to the same path as another team's team-scoped secret when the caller had no team context. A privileged caller without team context could therefore retrieve another team's secret by crafting a colliding `conn_id`. Fixed in 9.28.0 by switching the team-scope separator to `--` and rejecting team-shaped `conn_id`s when team context is absent. Affects the experimental multi-tenant teams feature only. Users are recommended to upgrade to `apache-airflow-providers-amazon` 9.28.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42526
- https://github.com/apache/airflow/pull/65703
- https://github.com/apache/airflow
- https://lists.apache.org/thread/0092sz5g520d3qqjb01wd61myqlgjtyn
- http://www.openwall.com/lists/oss-security/2026/05/19/36
