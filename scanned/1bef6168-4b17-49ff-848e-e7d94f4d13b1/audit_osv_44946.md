# [M] knowns through 0.33.0 Path Traversal via code.find MCP tool

## Summary
Severity: Medium
Advisory: CVE-2026-88938
Aliases: GHSA-5cj9-fcqq-g2h7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88938
Type: osv

## Details
knowns through 0.33.0 fails to confine the path argument of the code.find MCP tool to the project root, allowing AI agent sessions to read source files anywhere on the host. Attackers can supply absolute paths or relative traversal sequences to the path argument and retrieve full file contents from outside the intended project directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88938.json
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-5cj9-fcqq-g2h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-88938
- https://www.vulncheck.com/advisories/knowns-through-0.33.0-path-traversal-via-code-find-mcp-tool
- https://github.com/knowns-dev/knowns/blob/v0.33.0/internal/mcp/handlers/code.go#L1293-L1354
- https://github.com/knowns-dev/knowns/blob/v0.33.0/internal/mcp/handlers/code.go#L873-L902
