# [H] 9Router: Authenticated RCE via Unvalidated MCP Plugin Arguments

## Summary
Severity: High
Advisory: CVE-2026-62312
Aliases: GHSA-63p9-g54h-prrp
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-62312
Type: osv

## Details
9Router is an AI router & token saver. Prior to 0.5.2, 9Router allows a remote authenticated attacker to achieve arbitrary code execution on the host operating system by combining a Host header bypass of localhost-only routes with unvalidated MCP plugin args passed to child_process.spawn(), allowing malicious custom plugins to execute commands through /api/mcp//sse. This issue is fixed in version 0.5.2.

## References
- https://github.com/decolua/9router/releases/tag/v0.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62312.json
- https://github.com/decolua/9router/security/advisories/GHSA-63p9-g54h-prrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-62312
- https://github.com/decolua/9router/commit/da667836cc7584bea0edd893de1d590c9ea279dc
