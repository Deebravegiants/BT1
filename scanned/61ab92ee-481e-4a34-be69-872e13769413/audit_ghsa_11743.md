# [M] n8n has XSS in its Credential Management Flow

## Summary
Severity: Medium
Advisory: GHSA-364x-8g5j-x2pr
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-364x-8g5j-x2pr
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.7.0 <2.8.0
- npm: `n8n` — affected >=0 <2.6.4

## Details
## Impact
An authenticated user with permission to create and share credentials could craft a malicious OAuth2 credential containing a JavaScript URL in the Authorization URL field. If a victim opened the credential and interacted with the OAuth authorization button, the injected script would execute in their browser session.

## Patches
The issue has been fixed in n8n versions 2.8.0 and 2.6.4. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit credential creation and sharing permissions to fully trusted users only.
- Restrict access to the n8n instance to trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-364x-8g5j-x2pr
- https://github.com/n8n-io/n8n
