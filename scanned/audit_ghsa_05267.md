# [M] n8n: SQL Injection in Postgres v1/TimesclaeDB Nodes

## Summary
Severity: Medium
Advisory: GHSA-c37g-w77q-m4vp
CVE: CVE-2026-54310
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-c37g-w77q-m4vp
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=0 <2.25.7

## Details
## Impact
An authenticated user with permission to create or modify workflows could supply a crafted parameters to the TimescaleDB and/or legacy Postgres v1 node's allowing arbitrary SQL to be injected and executed against the connected database within the privileges of the configured database account.

## Patches
The issue has been fixed in n8n versions 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Postgres and TimescaleDB node by adding `n8n-nodes-base.postgres`,  `n8n-nodes-base.timescaleDb` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-c37g-w77q-m4vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-54310
- https://github.com/n8n-io/n8n
