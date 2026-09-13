# [M] MCP Java SDK has a Hardcoded Wildcard CORS (Access-Control-Allow-Origin: *)

## Summary
Severity: Medium
Advisory: GHSA-hv2w-8mjj-jw22
CVE: CVE-2026-34237
CWE: CWE-942
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-hv2w-8mjj-jw22
Type: github-advisory

## Affected
- Maven: `io.modelcontextprotocol.sdk:mcp-core` — affected >=1.0.0 <1.0.1
- Maven: `io.modelcontextprotocol.sdk:mcp-core` — affected >=1.1.0 <1.1.1
- Maven: `io.modelcontextprotocol.sdk:mcp-core` — affected >=0 <0.18.3

## Details
### Summary

**Hardcoded Wildcard CORS (Access-Control-Allow-Origin: * )**

- https://github.com/modelcontextprotocol/java-sdk/blob/main/mcp-core/src/main/java/io/modelcontextprotocol/server/transport/HttpServletSseServerTransportProvider.java#L289
- https://github.com/modelcontextprotocol/java-sdk/blob/main/mcp-core/src/main/java/io/modelcontextprotocol/server/transport/HttpServletStreamableServerTransportProvider.java#L525

### Attack Scenario
An attacker-controlled web page instructs the victim's browser to open GET https://internal-mcp-server/sse. Because Access-Control-Allow-Origin: * allows cross-origin SSE reads, the attacker's page receives the endpoint event — which contains the session ID. The attacker can then POST to that endpoint from their page using the victim's browser as a relay.

### Comparison with python-sdk
No Access-Control-Allow-Origin header is emitted by either Python transport. The browser's default same-origin policy remains in full effect.
https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/sse.py
https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/streamable_http.py

### Recommendation
In the SDK, the transport layer should not own CORS policy. Server implementors who need cross-origin access can add a CORS filter at the servlet filter or Spring Security layer.

### Reference

- https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html#access-control-allow-origin

## References
- https://github.com/modelcontextprotocol/java-sdk/security/advisories/GHSA-hv2w-8mjj-jw22
- https://nvd.nist.gov/vuln/detail/CVE-2026-34237
- https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html#access-control-allow-origin
- https://github.com/modelcontextprotocol/java-sdk
- https://github.com/modelcontextprotocol/java-sdk/blob/main/mcp-core/src/main/java/io/modelcontextprotocol/server/transport/HttpServletSseServerTransportProvider.java#L289
- https://github.com/modelcontextprotocol/java-sdk/blob/main/mcp-core/src/main/java/io/modelcontextprotocol/server/transport/HttpServletStreamableServerTransportProvider.java#L525
