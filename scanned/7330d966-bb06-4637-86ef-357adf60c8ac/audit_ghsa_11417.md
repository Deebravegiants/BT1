# [H] n8n has SQL Injection in Data Table Node via orderByColumn Expression

## Summary
Severity: High
Advisory: GHSA-98c2-4cr3-4jc3
CVE: CVE-2026-33713
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-98c2-4cr3-4jc3
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.26
- npm: `n8n` — affected >=2.14.0 <2.14.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.13.3

## Details
## Impact
An authenticated user with permission to create or modify workflows could exploit a SQL injection vulnerability in the Data Table Get node. On default SQLite DB, single statements can be manipulated and the attack surface is practically limited. On PostgreSQL deployments, multi-statement execution is possible, enabling data modification and deletion.

## Patches
The issue has been fixed in n8n versions 1.123.26, 2.13.3, and 2.14.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Data Table node by adding `n8n-nodes-base.dataTable` to the `NODES_EXCLUDE` environment variable.
- Review existing workflows for Data Table Get nodes where `orderByColumn` is set to an expression that incorporates external or user-supplied input.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-98c2-4cr3-4jc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33713
- https://github.com/n8n-io/n8n
