# [M] n8n has Webhook Forgery on Zendesk Trigger Node

## Summary
Severity: Medium
Advisory: GHSA-38c7-23hj-2wgq
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-38c7-23hj-2wgq
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.18
- npm: `n8n` — affected >=2.0.0 <2.6.2

## Details
## Impact
An attacker who knows the webhook URL of a workflow using the ZendeskTrigger node could send unsigned POST requests and trigger the workflow with arbitrary data. The node does not verify the HMAC-SHA256 signature that Zendesk attaches to every outbound webhook, allowing any party to inject crafted payloads into the connected workflow.

## Patches
The issue has been fixed in n8n versions 2.6.2 and 1.123.18. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Restrict network access to the n8n webhook endpoint to known Zendesk IP ranges.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-38c7-23hj-2wgq
- https://github.com/n8n-io/n8n/commit/3839e310bd4c3002c646c363d1411916fa195151
- https://github.com/n8n-io/n8n/commit/c6520e4e87614fa60c9433e93019e211f19f65f9
- https://github.com/n8n-io/n8n
