# [M] n8n: SSRF Protection Bypass via MCP Client Node

## Summary
Severity: Medium
Advisory: GHSA-vhf8-cg2h-cg3p
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-vhf8-cg2h-cg3p
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=0 <2.31.5

## Details
## Impact

On an n8n instance with SSRF protection enabled, the MCP Client node sent requests to a user-supplied endpoint without routing them through that protection and without pinning the resolved address. An authenticated user who could create or edit a workflow could therefore cause the server to connect to internal or otherwise blocked hosts and read the responses back through the workflow, exposing internal services the SSRF protection was meant to protect.

## Patches

The issue has been fixed in n8n versions 2.31.5 and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Disable the MCP Client node by adding it to the `NODES_EXCLUDE` environment variable.
- Restrict network egress from the n8n host to block access to internal and link-local address ranges at the network level.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-vhf8-cg2h-cg3p
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
