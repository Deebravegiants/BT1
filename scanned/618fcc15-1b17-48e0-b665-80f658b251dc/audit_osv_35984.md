# [C] CVE-2026-18482

## Summary
Severity: Critical
Advisory: CVE-2026-18482
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-18482
Type: osv

## Details
Neo.mjs contains a command injection vulnerability within the FileSystemService.mjs component of the ai/mcp/server/file-system MCP server, where the checkSyntax() and runPlaywrightTest() functions unsafely interpolate caller-controlled absolutePath values into shell commands, enabling arbitrary OS command execution when an AI agent is induced to invoke these tools. Commit 88c77fc fixes these vulnerabilities.

## References
- https://novice-22.com/posts/neo-mjs/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18482.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18482
- https://github.com/neomjs/neo/commit/5acc564ea1b278bca5fab1f8f397a6ba9b849d75
- https://github.com/neomjs/neo/commit/88c77fc4
