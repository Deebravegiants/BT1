# [H] mcp-handler has a tool response leak across concurrent client sessions ('Race Condition')

## Summary
Severity: High
Advisory: GHSA-w2fm-25vw-vh7f
CWE: CWE-1395, CWE-362
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-w2fm-25vw-vh7f
Type: github-advisory

## Affected
- npm: `mcp-handler` — affected >=0 <1.1.0

## Details
`mcp-handler` versions prior to 1.1.0 accepted `@modelcontextprotocol/sdk` < 1.26.0 as a peer dependency. That SDK version contains a vulnerability [[CVE-2026-25536](https://nvd.nist.gov/vuln/detail/CVE-2026-25536)] that causes concurrent requests from different clients to share server-side state including authentication context and tool execution results when a `StreamableHTTPServerTransport` instance is reused across requests.

**Note:** This is _not_ a vulnerability in `mcp-handler` itself. The root cause is in the peer dependency `@modelcontextprotocol/sdk`. 

### Impact

A low-privileged attacker making concurrent requests to an `mcp-handler` endpoint can read another client's session data, including authentication information and tool execution state. This is a confidentiality breach with potential for limited integrity impact.

**Root Cause:** [CVE-2026-25536](https://nvd.nist.gov/vuln/detail/CVE-2026-25536) in `@modelcontextprotocol/sdk` < 1.26.0. The SDK did not prevent reuse of stateless transports across client connections.

### Patches

Upgrade to `mcp-handler@1.1.0`. This release raises the minimum peer dependency to `@modelcontextprotocol/sdk@>=1.26.0`, which contains the fix for CVE-2026-25536. 

### Workarounds

- Upgrade `@modelcontextprotocol/sdk` to `>=1.26.0` (note: the SDK will throw on transport reuse, which will break `mcp-handler` < 1.1.0 which effectively forces the upgrade)
- Alternatively, manually create fresh `McpServer` and transport instances per request in your handler code

## References
- https://github.com/vercel/mcp-handler/security/advisories/GHSA-w2fm-25vw-vh7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25536
- https://github.com/advisories/GHSA-345p-7cg4-v4c7
- https://github.com/vercel/mcp-handler
