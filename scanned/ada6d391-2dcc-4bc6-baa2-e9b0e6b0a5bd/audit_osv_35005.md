# [H] CVE-2025-67366

## Summary
Severity: High
Advisory: CVE-2025-67366
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2025-67366
Type: osv

## Details
@sylphxltd/filesystem-mcp v0.5.8 is an MCP server that provides file content reading functionality. Version 0.5.8 of filesystem-mcp contains a critical path traversal vulnerability in its "read_content" tool. This vulnerability arises from improper symlink handling in the path validation mechanism: the resolvePath function checks path validity before resolving symlinks, while fs.readFile resolves symlinks automatically during file access. This allows attackers to bypass directory restrictions by leveraging symlinks within the allowed directory that point to external files, enabling unauthorized access to files outside the intended operational scope.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67366.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67366
- https://github.com/sylphxltd/filesystem-mcp/issues/134
- https://github.com/sylphxltd/filesystem-mcp
