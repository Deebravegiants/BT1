# [M] Apache Airflow's authenticated /ui/dags endpoint did not enforce per-DAG access control on embedded Human-in-the-Loop (HITL) and TaskInstance record

## Summary
Severity: Medium
Advisory: GHSA-p3v3-229h-mc63
CVE: CVE-2026-38743
CWE: CWE-1220
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-p3v3-229h-mc63
Type: github-advisory

## Affected
- PyPI: `apache-airflow` — affected >=0 <3.2.1rc1

## Details
The authenticated /ui/dags endpoint did not enforce per-DAG access control on embedded Human-in-the-Loop (HITL) and TaskInstance records: a logged-in Airflow user with read access to at least one DAG could retrieve HITL prompts (including their request parameters) and full TaskInstance details for DAGs outside their authorized scope. Because HITL prompts and TaskInstance fields routinely carry operator parameters and free-form context attached to a task, the leak widens visibility of DAG-run data beyond the intended per-DAG RBAC boundary for every authenticated user.

Users are recommended to upgrade to version 3.2.1 , which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-38743
- https://github.com/apache/airflow/pull/64822
- https://github.com/apache/airflow/commit/fed4921098d51fd3ec17b7f5cff80f6c36fd05e2
- https://github.com/apache/airflow
- https://lists.apache.org/thread/sk2wj0x48o8qb4p7c47gvnhjbm0mg396
- http://www.openwall.com/lists/oss-security/2026/04/24/3
