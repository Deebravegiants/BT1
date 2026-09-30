# [C] ForgeCode Arbitrary Code Execution via Unvetted .mcp.json in Untrusted Repository

## Summary
Severity: Critical
Advisory: CVE-2026-57860
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-57860
Type: osv

## Details
ForgeCode (tailcallhq/forgecode), an AI pair-programming CLI, automatically loads and executes the MCP servers defined in a repository's .mcp.json file on startup without user confirmation. A malicious repository can supply a crafted .mcp.json whose mcpServers entries specify arbitrary command and args values (for example, command: bash with args: ['-c', 'touch /tmp/pwned']). When a user runs the forge CLI inside a cloned untrusted repository, the specified commands are spawned with the invoking user's privileges, resulting in arbitrary code execution. This provides a reliable initial-access and persistence primitive against developers who evaluate untrusted repositories with ForgeCode.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57860.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-57860
- https://www.vulncheck.com/advisories/forgecode-arbitrary-code-execution-via-unvetted-mcp-json-in-untrusted-repository
- https://github.com/tailcallhq/forgecode/issues/3022
- https://github.com/tailcallhq/forgecode/issues/3252
- https://github.com/tailcallhq/forgecode/commit/68ca3a3a26c73c38a700453d3d021b5bbdc15dbd
- https://github.com/tailcallhq/forgecode
