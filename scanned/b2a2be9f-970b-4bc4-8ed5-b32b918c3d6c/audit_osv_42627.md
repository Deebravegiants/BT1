# [M] Apache Airflow Microsoft Azure provider: microsoft.azure Key Vault backend: team-scope guard bypass resolves another team's Connection or Variable

## Summary
Severity: Medium
Advisory: CVE-2026-68870
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68870
Type: osv

## Details
The Azure Key Vault secrets backend in Apache Airflow's Microsoft Azure provider resolved a team-scoped Connection or Variable id through the team-agnostic lookup when the team-scoped lookup missed. In a deployment running multi-team mode with this backend, a caller in one team could resolve a secret belonging to another team by supplying an id that spells out that team's namespace, obtaining its credentials in full. No unusual configuration is required beyond enabling multi-team mode and using this backend. Users are advised to upgrade to apache-airflow-providers-microsoft-azure 14.1.0 or later, which refuses the team-agnostic fall-through for an id that could name a team namespace.

## References
- http://www.openwall.com/lists/oss-security/2026/08/10/4
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68870.json
- https://lists.apache.org/thread/dtkk6vtfoj1y4zjyd6s3mzg0v5g9yg0p
- https://nvd.nist.gov/vuln/detail/CVE-2026-68870
- https://github.com/apache/airflow/pull/70876
- https://github.com/apache/airflow/pull/70899
