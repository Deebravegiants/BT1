# [M] Apache Airflow Amazon provider: amazon SSM / Secrets Manager backends: team-scope guard bypass resolves another team's Connection or Variable

## Summary
Severity: Medium
Advisory: CVE-2026-68872
Aliases: PYSEC-2026-3713
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68872
Type: osv

## Details
The AWS Systems Manager Parameter Store and Secrets Manager backends in Apache Airflow's Amazon provider resolved a team-scoped Connection or Variable id through the team-agnostic lookup when the team-scoped lookup missed. In a deployment running multi-team mode with either backend, a caller in one team could resolve a secret belonging to another team by supplying an id that spells out that team's namespace, obtaining its credentials in full. No unusual configuration is required beyond enabling multi-team mode and using one of these backends. Users are advised to upgrade to apache-airflow-providers-amazon 9.34.0 or later, which refuses the team-agnostic fall-through for an id that could name a team namespace.

## References
- http://www.openwall.com/lists/oss-security/2026/08/10/6
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68872.json
- https://lists.apache.org/thread/9nd31g40rd2zpgwwymskvjpfq1xnmllg
- https://nvd.nist.gov/vuln/detail/CVE-2026-68872
- https://github.com/apache/airflow/pull/70878
