# [M] n8n: SQL Injection in MySQL, PostgreSQL, and Microsoft SQL nodes

## Summary
Severity: Medium
Advisory: GHSA-f3f2-mcxc-pwjx
CVE: CVE-2026-56351
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-f3f2-mcxc-pwjx
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.4.0

## Details
## Impact
An authenticated user with permission to create or modify workflows and access to a database credential could unknowingly create a workflow that was vulnerable to SQL injection, even while expecting inputs to be handled safely through escaped parameters. By supplying specially crafted table or column names, an attacker could inject arbitrary SQL because the MySQL, PostgreSQL, and Microsoft SQL nodes did not escape identifier values when constructing queries, enabling injection through node configuration parameters.

## Patches
The issue has been fixed in n8n version 2.4.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the MySQL, PostgreSQL, and Microsoft SQL nodes by adding `n8n-nodes-base.mySql`, `n8n-nodes-base.postgres`, and `n8n-nodes-base.microsoftSql` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## Credit

Reporter: Pawel Bednarz from the NATO Cyber Security Centre (NCSC)

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-f3f2-mcxc-pwjx
- https://nvd.nist.gov/vuln/detail/CVE-2026-56351
- https://github.com/n8n-io/n8n/commit/f73fae6fe7fc34907bba102648a9997186aa4385
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.4.0
- https://www.vulncheck.com/advisories/n8n-sql-injection-in-mysql-postgresql-and-microsoft-sql-nodes
