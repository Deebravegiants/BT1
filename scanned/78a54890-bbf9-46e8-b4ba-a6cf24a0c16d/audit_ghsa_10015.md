# [H] Java-SDK has a DNS Rebinding Vulnerability

## Summary
Severity: High
Advisory: GHSA-8jxr-pr72-r468
CVE: CVE-2026-35568
CWE: CWE-346
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-8jxr-pr72-r468
Type: github-advisory

## Affected
- Maven: `io.modelcontextprotocol.sdk:mcp-core` — affected >=0 <1.0.0

## Details
### Summary

The java-sdk contains a DNS rebinding vulnerability. This vulnerability allows an attacker to access a locally or network-private java-sdk MCP server via a victims browser that is either local, or network adjacent.

This allows an attacker to make any tool call to the server as if they were a locally running MCP connected AI agent.

### Details

Prior to 1.0.0 no Origin header validation was occurring, in violation of the MCP specification. [Base Protocol > Transports: 2.0.1 Security Warning](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#security-warning):

> 1: Servers MUST validate the Origin header on all incoming connections to prevent DNS rebinding attacks.

When the web server serving HTTP traffic to the MCP server does not perform standard CORS checks, a DNS rebinding attack is possible.

Some default server configurations and frameworks come with embedded `Origin` header validation. MCP servers built using those are not vulnerable to this issue. For example, the following are NOT vulnerable:
- Spring AI

### Impact

Any developer connecting to a malicious website can inadvertently allow an attacker to make tool calls to local or private-network MCP servers.

### Workarounds

Users can mitigate this risk by:
1. Running the MCP server behind a reverse proxy (like Nginx or HAProxy) configured to strictly validate the `Host` and `Origin` headers.
2. Using a framework that inherently enforces strict CORS and Origin validation (such as Spring AI).

## References
- https://github.com/modelcontextprotocol/java-sdk/security/advisories/GHSA-8jxr-pr72-r468
- https://nvd.nist.gov/vuln/detail/CVE-2026-35568
- https://github.com/modelcontextprotocol/java-sdk
- https://github.com/modelcontextprotocol/java-sdk/releases/tag/v1.0.0
