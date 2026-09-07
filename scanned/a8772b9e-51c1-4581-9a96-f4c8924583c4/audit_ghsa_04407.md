# [H] n8n: Same-Origin XSS in Respond to Webhook Node

## Summary
Severity: High
Advisory: GHSA-v733-mwr6-fgcm
CVE: CVE-2026-54301
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-v733-mwr6-fgcm
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.55
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=2.0.0-rc.0 <2.25.7

## Details
## Impact
An authenticated user with workflow edit access could configure a `Respond to Webhook` node to serve binary content with an attacker-controlled `Content-Type`. The binary response path bypassed the central `Content-Security-Policy` sandbox header, allowing a public webhook to execute JavaScript in the n8n origin when visited by an authenticated user, with access to that user's session.

## Patches
The issue has been fixed in n8n versions 1.123.55, 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Respond to Webhook node by adding `n8n-nodes-base.respondToWebhook` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-v733-mwr6-fgcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54301
- https://github.com/n8n-io/n8n
