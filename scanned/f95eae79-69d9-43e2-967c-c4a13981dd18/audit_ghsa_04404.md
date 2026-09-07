# [H] n8n: Stored XSS in Chat Trigger Node

## Summary
Severity: High
Advisory: GHSA-42h7-m79w-wvg5
CVE: CVE-2026-54302
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-42h7-m79w-wvg5
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.55
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=2.0.0-rc.0 <2.25.7

## Details
## Impact
An authenticated user with workflow edit access could inject arbitrary JavaScript into the Chat Trigger's generated page by setting a malicious `webhookId`. When a logged-in user visited the chat URL, the injected code executed in the n8n origin with that user's session privileges.

## Patches
The issue has been fixed in n8n versions 1.123.55, 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Chat Trigger node by adding `@n8n/n8n-nodes-langchain.chatTrigger` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-42h7-m79w-wvg5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54302
- https://github.com/n8n-io/n8n
