# [M] Markdownify MCP Server allows attackers to read arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-22v8-p7h2-rj7p
CVE: CVE-2025-5273
CWE: CWE-552
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-29
Source: https://github.com/advisories/GHSA-22v8-p7h2-rj7p
Type: github-advisory

## Affected
- npm: `mcp-markdownify-server` — affected >=0

## Details
All versions of the package mcp-markdownify-server are vulnerable to Files or Directories Accessible to External Parties via the get-markdown-file tool. An attacker can craft a prompt that, once accessed by the MCP host, will allow it to read arbitrary files from the host running the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5273
- https://github.com/zcaceres/markdownify-mcp/commit/3a6b202d088ef7acb8be84bc09515f41a2b1a9df
- https://github.com/zcaceres/markdownify-mcp
- https://github.com/zcaceres/markdownify-mcp/blob/3667bd4765c0e49684ce22df268d02dd478a7f3b/src/Markdownify.ts#L94
- https://security.snyk.io/vuln/SNYK-JS-MCPMARKDOWNIFYSERVER-10249193
