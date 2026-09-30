# [H] Roslyn CodeLens MCP Server: Untrusted Roslyn Analyzer Execution via get_diagnostics Leads to Arbitrary Code Execution

## Summary
Severity: High
Advisory: CVE-2026-45555
Aliases: GHSA-552p-8f74-6x7q
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45555
Type: osv

## Details
Roslyn CodeLens MCP Server is a Roslyn-based MCP server providing semantic code intelligence for .NET codebases. From 0.0.9 to 1.17.0, the get_diagnostics MCP tool loads and executes all DiagnosticAnalyzer assemblies referenced by the target solution without any allowlist, signature check, or user confirmation; includeAnalyzers defaults to true, so no explicit opt-in is required. An attacker who can place a malicious .csproj referencing an attacker-controlled DLL in a location the victim opens with the MCP server will achieve arbitrary code execution in the server process with the server's OS privileges. This vulnerability is fixed in 1.17.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45555.json
- https://github.com/MarcelRoozekrans/roslyn-codelens-mcp/security/advisories/GHSA-552p-8f74-6x7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-45555
