# [C] knowns before 0.30.0 Path Traversal via MCP doc and memory tools

## Summary
Severity: Critical
Advisory: CVE-2026-86439
Aliases: GHSA-9gfj-28hw-jchp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86439
Type: osv

## Details
knowns versions before 0.30.0 fail to validate filesystem paths in MCP tool arguments, allowing attackers to read, create, overwrite and delete files outside the project directory. Attackers can supply path arguments containing directory traversal sequences to access arbitrary Markdown files accessible to the server process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86439.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.30.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-9gfj-28hw-jchp
- https://nvd.nist.gov/vuln/detail/CVE-2026-86439
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-path-traversal-via-mcp-doc-and-memory-tools
- https://github.com/knowns-dev/knowns/commit/09c5a96fd5817b941dc86669278c1a17db10ed4e
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/storage/doc_store.go#L124-L129
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/storage/memory_store.go#L203-L211
