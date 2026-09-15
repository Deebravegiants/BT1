# [M] n8n has an Authentication Bypass in its Chat Trigger Node

## Summary
Severity: Medium
Advisory: GHSA-jh8h-6c9q-7gmw
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-jh8h-6c9q-7gmw
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.22
- npm: `n8n` — affected >=2.0.0 <2.9.3
- npm: `n8n` — affected >=2.10.0 <2.10.1

## Details
## Impact
When the Chat Trigger node is configured with n8n User Auth authentication, the authentication check could be circumvented. 
- This issue requires the Chat Trigger node to be configured with n8n User Auth authentication (non-default).

## Patches
The issue has been fixed in n8n versions 2.10.1, 2.9.3, and 1.123.22. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Use a different authentication method for the Chat Trigger node, or restrict network access to the webhook endpoint to trusted origins.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jh8h-6c9q-7gmw
- https://github.com/n8n-io/n8n/commit/062644ef786b6af480afe4a0f12bc6d70040534a
- https://github.com/n8n-io/n8n/commit/1479aab2d32fe0ee087f82b9038b1035c98be2f6
- https://github.com/n8n-io/n8n/commit/9e5212ecbc5d2d4e6f340b636a5e84be6369882e
- https://github.com/n8n-io/n8n
