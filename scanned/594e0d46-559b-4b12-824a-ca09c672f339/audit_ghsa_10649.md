# [M] n8n has Open Redirect in MCP OAuth Consent Flow

## Summary
Severity: Medium
Advisory: GHSA-f6x8-65q6-j9m9
CVE: CVE-2026-42230
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-f6x8-65q6-j9m9
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.0.0 <2.17.4

## Details
## Impact
The `/mcp-oauth/register` endpoint accepted OAuth client registrations without authentication, allowing arbitrary `redirect_uri` values to be registered. When a user denies the MCP OAuth consent dialog, the `handleDeny` handler redirects the user to the registered `redirect_uri` without validation, enabling an open redirect to an attacker-controlled URL. An attacker can craft a phishing link and send it to a victim; if the victim clicks "Deny" on the consent page, they are silently redirected to an external site.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict network access to the n8n instance to prevent untrusted users from reaching the MCP OAuth endpoints.
- Limit access to the n8n instance to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-f6x8-65q6-j9m9
- https://nvd.nist.gov/vuln/detail/CVE-2026-42230
- https://github.com/n8n-io/n8n
