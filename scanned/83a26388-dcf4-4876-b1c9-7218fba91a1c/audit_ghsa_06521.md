# [M] n8n: MySQL v1 Node executeQuery Operation Allows SQL Injection via Unparameterized Expression Interpolation

## Summary
Severity: Medium
Advisory: GHSA-hwmj-qg4v-cvg9
CVE: CVE-2026-59257
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-hwmj-qg4v-cvg9
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.61
- npm: `n8n` — affected >=2.28.0 <2.28.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.27.4

## Details
## Impact
The legacy MySQL v1 node's `executeQuery` operation substitutes evaluated `{{ ... }}` expression values directly into the raw SQL string without parameterization. If a workflow uses this operation with expression-sourced values in the query and is connected to an externally-reachable trigger (such as a Webhook node), attacker-controlled input reaching those expressions results in SQL injection.

Successful exploitation allows arbitrary SQL execution with the configured MySQL credentials' privileges, enabling unauthorized disclosure, modification, or deletion of data in the downstream database. MySQL v2 node is not affected.

This issue can affect only instances running workflows that use the MySQL v1 node with `executeQuery` operations.

## Patches
The issue has been fixed in n8n versions 1.123.61, 2.27.4, and 2.28.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the MySQL node by adding `n8n-nodes-base.mySql` to the `NODES_EXCLUDE` environment variable, or audit and restrict access to workflows using the MySQL v1 node with the `executeQuery` operation.
- Ensure that webhook endpoints used in workflows containing MySQL v1 `executeQuery` nodes with expression interpolation require authentication.
- Migrate affected workflows to use the MySQL v2 node, which uses parameterized queries.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hwmj-qg4v-cvg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-59257
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.61
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.28.1
- https://www.vulncheck.com/advisories/n8n-sql-injection-in-mysql-v1-executequery-operation-via-expression-interpolation
