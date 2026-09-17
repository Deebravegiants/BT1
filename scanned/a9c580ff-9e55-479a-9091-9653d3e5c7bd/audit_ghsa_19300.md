# [M] Markdownify MCP Server allows Server-Side Request Forgery (SSRF) via the Markdownify.get() function

## Summary
Severity: Medium
Advisory: GHSA-frq9-3hp2-xvxg
CVE: CVE-2025-5276
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-29
Source: https://github.com/advisories/GHSA-frq9-3hp2-xvxg
Type: github-advisory

## Affected
- npm: `mcp-markdownify-server` — affected >=0

## Details
All versions of the package mcp-markdownify-server are vulnerable to Server-Side Request Forgery (SSRF) via the Markdownify.get() function. An attacker can craft a prompt that, once accessed by the MCP host, can invoke the webpage-to-markdown, bing-search-to-markdown, and youtube-to-markdown tools to issue requests and read the responses to attacker-controlled URLs, potentially leaking sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5276
- https://github.com/zcaceres/markdownify-mcp/commit/0284aa8f34d32c65e20d8cda2d429b7943c9af03
- https://github.com/zcaceres/markdownify-mcp
- https://github.com/zcaceres/markdownify-mcp/blob/224cf89f0d58616d2a5522f60f184e8391d1c9e3/src/server.ts#L20C17-L20C29
- https://security.snyk.io/vuln/SNYK-JS-MCPMARKDOWNIFYSERVER-10249387
