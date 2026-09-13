# [H] n8n: "Allowed HTTP Request Domains" Restriction Bypass via AI Agents MCP Connector

## Summary
Severity: High
Advisory: GHSA-h44j-f5r5-ph73
CVE: CVE-2026-59207
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-h44j-f5r5-ph73
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.28.0 <2.28.1
- npm: `n8n` — affected >=0 <2.27.4

## Details
## Impact
The AI Agents feature did not enforce the "Allowed HTTP Request Domains" restriction configured on credentials. As a result, a member-level user who had been granted use-only access to a shared credential could cause its secret to be sent to an external server they control, by pointing an MCP tool at an arbitrary URL and running the agent.

This issue only affects instances where the AI Agents module is enabled via `N8N_ENABLED_MODULES=agents` and at least one credential with domain restrictions has been shared with a member-level user.

## Patches
The issue has been fixed in n8n version 2.28.1 and 2.27.4. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Disable the AI Agents module by removing `agents` from the `N8N_ENABLED_MODULES` environment variable.
- Restrict credential sharing to fully trusted users only.
- Audit credentials with domain restrictions for unexpected sharing relationships.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-h44j-f5r5-ph73
- https://nvd.nist.gov/vuln/detail/CVE-2026-59207
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.28.1
