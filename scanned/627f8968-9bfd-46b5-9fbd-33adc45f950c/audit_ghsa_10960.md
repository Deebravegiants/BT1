# [H] Cross-Site Tool Execution for HTTP Servers without Authorizatrion in github.com/modelcontextprotocol/go-sdk

## Summary
Severity: High
Advisory: GHSA-89xv-2j6f-qhc8
CVE: CVE-2026-33252
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-89xv-2j6f-qhc8
Type: github-advisory

## Affected
- Go: `github.com/modelcontextprotocol/go-sdk` — affected >=0 <1.4.1

## Details
The Go SDK's Streamable HTTP transport accepted browser-generated cross-site `POST` requests without validating the `Origin` header and without requiring `Content-Type: application/json`. In deployments without Authorization, especially stateless or sessionless configurations, this allows an arbitrary website to send MCP requests to a local server and potentially trigger tool execution.

#### Impact:

A malicious website may have been able to send cross-site POST requests with `Content-Type: text/plain`, which due to CORS-safelisted properties would reach the MCP message handling without any CORS preflight barrier.

#### Fix:

The SDK was modified to perform `Content-Type` header validation for POST requests and introduced a configurable protection for verifying the origin of the request in commit a433a83. Users are advised to update to v1.4.1 to use this additional protection.

Note: v1.4.1 requires Go 1.25 or later.

#### Credits:

Thank you to Lê Minh Quân for reporting the issue.

## References
- https://github.com/modelcontextprotocol/go-sdk/security/advisories/GHSA-89xv-2j6f-qhc8
- https://nvd.nist.gov/vuln/detail/CVE-2026-33252
- https://github.com/modelcontextprotocol/go-sdk/commit/a433a831d6e5d5ac3b9e625a8095aa8eaa040dfc
- https://github.com/modelcontextprotocol/go-sdk
