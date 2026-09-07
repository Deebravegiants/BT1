# [H] n8n: Shared-Workflow Editor Can Exfiltrate Credentials via Inline Sub-Workflow JSON

## Summary
Severity: High
Advisory: GHSA-cj9h-qx8g-pq2g
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-cj9h-qx8g-pq2g
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.67
- npm: `n8n` — affected >=2.32.0 <2.32.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.31.5

## Details
## Impact

n8n's credential-access checks validated only a node's top-level credentials, not credentials referenced inside an Execute Sub-workflow node's inline workflow JSON. A member with editor access to a shared workflow could reference a credential they were not permitted to use inside that inline JSON; it passed both save-time and runtime validation and resolved in the parent workflow's project context, letting the member use or exfiltrate a credential they could not otherwise access.

Exploitation requires workflow sharing to be enabled and the attacker to have been explicitly granted Editor access to a shared workflow. The attacker must also know the target credential's ID.

## Patches

The issue has been fixed in n8n versions 1.123.67, 2.31.5, and 2.32.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds

If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow sharing to fully trusted users only, and avoid granting Editor access to untrusted members on workflows that use sensitive credentials.
- Audit shared workflows for Execute Sub-workflow nodes with Source = "Parameter" and review their inline workflow definitions for unexpected credential references.
- Restrict network egress from the n8n instance to prevent connections to attacker-controlled endpoints.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-cj9h-qx8g-pq2g
- https://github.com/n8n-io/n8n/commit/f69dfc6dd2178a14ea1624d2e1d403c2e755042f
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.67
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.31.5
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.32.1
