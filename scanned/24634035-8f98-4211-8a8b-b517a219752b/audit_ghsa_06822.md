# [M] n8n: PostgresTrigger Node SQL Injection Allows Authenticated Users to Execute Arbitrary SQL on Connected PostgreSQL Instances

## Summary
Severity: Medium
Advisory: GHSA-jqwr-vx3p-r266
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-jqwr-vx3p-r266
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.67
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.31.5

## Details
## Impact

The Postgres Trigger node interpolated user-supplied identifier parameters (channel, function, and trigger names) into SQL statements without proper escaping, so an authenticated user could inject arbitrary SQL executed against the connected PostgreSQL database with the configured credential's privileges.

Successful exploitation allows full read and write access to the connected PostgreSQL database. 

## Patches

The issue has been fixed in n8n versions 1.123.67, 2.31.5 and 2.32.1. Users should upgrade to these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable the PostgresTrigger node by adding `n8n-nodes-base.postgresTrigger` to the `NODES_EXCLUDE` environment variable.
- Ensure PostgreSQL credentials used with n8n are configured with the minimum required privileges and do not use SUPERUSER roles.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jqwr-vx3p-r266
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.67
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
