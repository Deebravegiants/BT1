# [H] Spring AI MCP Security: Unvalidated URL Fetching (SSRF)

## Summary
Severity: High
Advisory: GHSA-qjp4-4jvr-xqg3
CVE: CVE-2026-45609
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-qjp4-4jvr-xqg3
Type: github-advisory

## Affected
- Maven: `org.springaicommunity:mcp-client-security` — affected >=0 <0.1.9

## Details
### Summary

The mcp-security framework fails to implement the mandatory SSRF mitigations outlined in the Model Context Protocol (MCP) [security specifications](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices#mitigation-3). Specifically, it processes untrusted URLs for OAuth-related discovery and metadata without verifying if the targets are malicious or internal to the network.

This only affects installations with Dynamic Client Registration (DCR) enabled:

```properties
spring.ai.mcp.client.authorization.dynamic-client-registration.enabled=true
```

DCR does not validate URLs exposed by MCP Servers (protected resource metadata URL, authorization server URL) and Authorization Servers (all OAuth2 endpoints).

### Workaround

When users need to perform DCR, they may provide their own `McpOAuth2ClientManager`. Both `McpMetadataDiscoveryService` and `DynamicClientRegistrationService` are also affected, if used, users should provide their own subclasses.

Alternatively, users can provide the default implementations of these classes with a `RestClient` that implements URL filtering through `ClientHttpRequestInterceptor`.

## References
- https://github.com/spring-ai-community/mcp-security/security/advisories/GHSA-qjp4-4jvr-xqg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45609
- https://github.com/spring-ai-community/mcp-security/pull/68
- https://github.com/spring-ai-community/mcp-security/commit/e6b67d8a67cd7acbee6e4c0741c385d62e3ed576
- https://github.com/spring-ai-community/mcp-security
- https://github.com/spring-ai-community/mcp-security/releases/tag/v0.1.9
