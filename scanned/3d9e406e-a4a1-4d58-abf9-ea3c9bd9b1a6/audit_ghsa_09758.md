# [M] n8n has SQL Injection in Snowflake and MySQL Nodes

## Summary
Severity: Medium
Advisory: GHSA-hp3c-vfpm-q4f7
CVE: CVE-2026-42237
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-hp3c-vfpm-q4f7
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.0.0 <2.17.4

## Details
## Impact
The fix for [GHSA-f3f2-mcxc-pwjx](https://github.com/advisories/GHSA-f3f2-mcxc-pwjx) did not cover the Snowflake node or the legacy MySQL v1 node. Both nodes construct SQL queries by directly interpolating user-controlled table names, column names, and update keys into query strings without identifier escaping, enabling SQL injection against the connected database.

Exploitation requires a specific workflow configuration:
- The Snowflake or MySQL v1 node must be used with user-controlled input passed via expressions (e.g., from a form or webhook) into identifier fields such as table name, column name, or update key.

Successful exploitation could allow data exfiltration, modification, or deletion on the downstream database.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Migrate workflows from the legacy MySQL v1 node to the MySQL v2 node, which already implements identifier escaping.
- Disable the Snowflake node by adding `n8n-nodes-base.snowflake` to the `NODES_EXCLUDE` environment variable.
- Avoid passing unvalidated external user input into table name, column name, or update key fields via expressions in the affected nodes.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-f3f2-mcxc-pwjx
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hp3c-vfpm-q4f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42237
- https://github.com/n8n-io/n8n
