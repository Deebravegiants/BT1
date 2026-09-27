# [H] Apache Superset: Improper authorization bypass on row level security via SQL Injection

## Summary
Severity: High
Advisory: GHSA-8w7f-8pr9-xgwj
CVE: CVE-2025-48912
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-30
Source: https://github.com/advisories/GHSA-8w7f-8pr9-xgwj
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <4.1.2

## Details
An authenticated malicious actor using specially crafted requests could bypass row level security configuration by injecting SQL into 'sqlExpression' fields. This allowed the execution of sub-queries to evade parsing defenses ultimately granting unauthorized access to data.

This issue affects Apache Superset: before 4.1.2.

Users are recommended to upgrade to version 4.1.2, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48912
- https://github.com/apache/superset
- https://lists.apache.org/thread/ms2t2oq218hb7l628trsogo4fj7h1135
- http://www.openwall.com/lists/oss-security/2025/05/30/3
