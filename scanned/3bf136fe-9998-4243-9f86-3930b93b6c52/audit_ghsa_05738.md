# [H] Anthropic's MCP TypeScript SDK has a ReDoS vulnerability

## Summary
Severity: High
Advisory: GHSA-8r9q-7v3j-jr4g
CVE: CVE-2026-0621
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-8r9q-7v3j-jr4g
Type: github-advisory

## Affected
- npm: `@modelcontextprotocol/sdk` — affected >=1.3.0 <1.25.2

## Details
### Impact

A ReDoS vulnerability in the `UriTemplate` class allows attackers to cause denial of service. The `partToRegExp()` function generates a regex pattern with nested quantifiers (`([^/]+(?:,[^/]+)*)`) for exploded template variables (e.g., `{/id*}`, `{?tags*}`), causing catastrophic backtracking on malicious input.

**Who is affected:** MCP servers that register resource templates with exploded array patterns and accept requests from untrusted clients.

**Attack result:** An attacker sends a crafted URI via `resources/read` request, causing 100% CPU utilization, server hang/crash, and denial of service for all clients.

### Affected Versions

All versions of `@modelcontextprotocol/sdk` prior to the patched release.

### Patches

v1.25.2 contains b392f02ffcf37c088dbd114fedf25026ec3913d3 the fix modifies the regex pattern to prevent backtracking.

### Workarounds

- Avoid using exploded patterns (`{/id*}`, `{?tags*}`) in resource templates
- Implement request timeouts and rate limiting
- Validate URIs before processing to reject suspicious patterns

## References
- https://github.com/modelcontextprotocol/typescript-sdk/security/advisories/GHSA-cqwc-fm46-7fff
- https://nvd.nist.gov/vuln/detail/CVE-2026-0621
- https://github.com/modelcontextprotocol/typescript-sdk/issues/965
- https://github.com/modelcontextprotocol/typescript-sdk/commit/7f0cf730
- https://github.com/modelcontextprotocol/typescript-sdk/commit/b392f02ffcf37c088dbd114fedf25026ec3913d3
- https://github.com/modelcontextprotocol/typescript-sdk
- https://github.com/modelcontextprotocol/typescript-sdk/releases/tag/v1.25.2
- https://www.vulncheck.com/advisories/mcp-typescript-sdk-uritemplate-exploded-array-pattern-redos
