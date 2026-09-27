# [M] Agentgateway is missing parameter sanitization in MCP to OpenAPI conversion

## Summary
Severity: Medium
Advisory: GHSA-v2x6-wwfw-r2rq
CVE: CVE-2026-29791
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-v2x6-wwfw-r2rq
Type: github-advisory

## Affected
- Go: `github.com/agentgateway/agentgateway` — affected >=0 <0.12.0

## Details
### Summary

When converting MCP `tools/call` request to OpenAPI request, input path, query, and header values are not sanitized.

### Details

When using the [MCP to OpenAPI](https://agentgateway.dev/docs/standalone/latest/mcp/connect/openapi/) feature, the proxy lacks proper sanitization of input parameters in the MCP call, allowing:
* Injection of additional path or query parameters.
* Injection of additional headers.

### Impacted Versions

This vulnerability is fixed in Agentgateway v0.12.0+. Users on older versions are recommended to upgrade to v0.12.0+.

This feature only impacts usage of the [MCP to OpenAPI](https://agentgateway.dev/docs/standalone/latest/mcp/connect/openapi/) feature

### Credits

Agentgateway extends its thanks to @spacewander for the report!

## References
- https://github.com/agentgateway/agentgateway/security/advisories/GHSA-v2x6-wwfw-r2rq
- https://nvd.nist.gov/vuln/detail/CVE-2026-29791
- https://github.com/agentgateway/agentgateway/commit/9a5287569d892e77a8be8c3bb7bf3d7744244274
- https://github.com/agentgateway/agentgateway
