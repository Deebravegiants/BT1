# [M] Apache Airflow Google provider: google Secret Manager backend: team scope is never applied, exposing every team's Connections and Variables

## Summary
Severity: Medium
Advisory: CVE-2026-68868
Aliases: PYSEC-2026-3714
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68868
Type: osv

## Details
The Google Cloud Secret Manager secrets backend in Apache Airflow's Google provider never applied the team scope when resolving Connections and Variables: the caller's `team_name` was accepted by the backend but dropped at the internal call boundary, so every lookup resolved against the team-agnostic secret name. In a deployment running multi-team mode with this backend, a task or Dag belonging to one team resolved another team's Connection or Variable, obtaining its credentials in full. No unusual configuration is required beyond enabling multi-team mode and using this backend. Users are advised to upgrade to apache-airflow-providers-google 22.3.0 or later, which builds and applies the team-scoped secret name.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/3
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68868.json
- https://lists.apache.org/thread/03h5y0fmqlh0yf055zlocxh591ozx69x
- https://nvd.nist.gov/vuln/detail/CVE-2026-68868
- https://github.com/apache/airflow/pull/70869
