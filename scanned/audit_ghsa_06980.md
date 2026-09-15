# [M] n8n: Member-Level Users Can Execute Other Users' MCP Server Trigger Workflows via Missing OAuth Authorization Check

## Summary
Severity: Medium
Advisory: GHSA-q5xf-xhwf-cwqf
CVE: CVE-2026-65594
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-q5xf-xhwf-cwqf
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=0 <2.29.8

## Details
## Impact
The OAuth 2.1 consent and token-issuance flow introduced in n8n 2.27.0 does not verify that the authenticated user has access to the workflow referenced as the OAuth resource. A member-level user can register an OAuth client, self-approve consent for another user's `n8n OAuth2`-protected MCP Server Trigger workflow, and obtain a valid token for it.

The workflow runs in the owner's project context with the owner's stored credentials. The attacker sets the tool inputs and reads the outputs, which may include data from the owner's connected integrations, breaking user and project isolation. The resulting executions appear under the owner's account and are not visible to the attacker.

This issue only affects instances running n8n 2.27.0 or later where at least one active workflow uses an MCP Server Trigger node configured with `n8n OAuth2` authentication.

## Patches
The issue has been fixed in n8n versions 2.29.8 and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict n8n instance access to fully trusted users only.
- Audit active workflows using the MCP Server Trigger with `n8n OAuth2` authentication and consider switching to a different authentication method or deactivating them until the patch is applied.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-q5xf-xhwf-cwqf
- https://nvd.nist.gov/vuln/detail/CVE-2026-65594
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-missing-oauth-authorization-check
