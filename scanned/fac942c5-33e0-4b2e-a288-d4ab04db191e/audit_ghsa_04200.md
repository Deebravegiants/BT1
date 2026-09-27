# [H] n8n: MCP Browser HTTP Transport Exposes Unauthenticated Browser-Control Sessions

## Summary
Severity: High
Advisory: GHSA-qrx8-25qr-5r7v
CVE: CVE-2026-54309
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-qrx8-25qr-5r7v
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=0 <2.25.7

## Details
## Impact
When `@n8n/mcp-browser` is run in HTTP transport mode, the MCP endpoint accepts session initialization and tool invocation requests without any authentication. Any network-reachable client, or any website visited by the user, can establish an MCP session and invoke browser-control tools.

Where the n8n AI Browser Bridge extension is installed and a browser connection is active, an unauthenticated caller can access browser-control capabilities including navigation, JavaScript evaluation, and cookie and storage access against the user's real browser profile.

This issue only affects instances where `@n8n/mcp-browser` is run with the HTTP transport (`--transport http`). The default transport is stdio, which is not affected.

## Patches
The issue has been fixed in n8n versions 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Avoid running `@n8n/mcp-browser` with the HTTP transport; use the default stdio transport instead.
- If HTTP transport is required, restrict network access to the listening port to trusted clients only using host-based firewall rules.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-qrx8-25qr-5r7v
- https://nvd.nist.gov/vuln/detail/CVE-2026-54309
- https://github.com/n8n-io/n8n
