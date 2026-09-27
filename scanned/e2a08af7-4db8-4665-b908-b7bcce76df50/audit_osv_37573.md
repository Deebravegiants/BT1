# [H] LibreChat MCP OAuth callback does not validate browser session — allows token theft via redirect link

## Summary
Severity: High
Advisory: CVE-2026-31944
Aliases: GHSA-vf7j-7mrx-hp7g
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31944
Type: osv

## Details
LibreChat is a ChatGPT clone with additional features. From 0.8.2 to 0.8.2-rc3, The MCP (Model Context Protocol) OAuth callback endpoint accepts the redirect from the identity provider and stores OAuth tokens for the user who initiated the flow, without verifying that the browser hitting the redirect URL is logged in or that the logged-in user matches the initiator. An attacker can send the authorization URL to a victim; when the victim completes the flow, the victim’s OAuth tokens are stored on the attacker’s LibreChat account, enabling account takeover of the victim’s MCP-linked services (e.g. Atlassian, Outlook). This vulnerability is fixed in 0.8.3-rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31944.json
- https://github.com/danny-avila/LibreChat/security/advisories/GHSA-vf7j-7mrx-hp7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-31944
