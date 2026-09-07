# [M] n8n has XSS in Chat Trigger Node through Custom CSS

## Summary
Severity: Medium
Advisory: GHSA-3c7f-5hgj-h279
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-3c7f-5hgj-h279
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.27
- npm: `n8n` — affected >=2.14.0 <2.14.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.13.3

## Details
## Impact
An authenticated user with permission to create or modify workflows could inject malicious JavaScript into the Custom CSS field of the Chat Trigger node. Due to a misconfiguration in the `sanitize-html` library, the sanitization could be bypassed, resulting in stored XSS on the public chat page. Any user visiting the chat URL would be affected.

## Patches
The issue has been fixed in n8n versions 1.123.27, 2.13.3, and 2.14.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Chat Trigger node by adding `@n8n/n8n-nodes-langchain.chatTrigger` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-3c7f-5hgj-h279
- https://github.com/n8n-io/n8n
