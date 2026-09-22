# [H] JunoClaw: upload_wasm accepted arbitrary filesystem paths without validation

## Summary
Severity: High
Advisory: CVE-2026-43989
Aliases: GHSA-rw59-34hw-pmwp
CVSS: 8.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-43989
Type: osv

## Details
JunoClaw is an agentic AI platform built on Juno Network. Prior to 0.x.y-security-1, the upload_wasm MCP tool accepted a filesystem path from the agent and uploaded whatever bytes the path resolved to, with no validation of location, symlink target, file size, or file format. This vulnerability is fixed in 0.x.y-security-1.

## References
- https://github.com/Dragonmonk111/junoclaw/releases/tag/v0.x.y-security-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43989.json
- https://github.com/Dragonmonk111/junoclaw/security/advisories/GHSA-rw59-34hw-pmwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-43989
- https://github.com/Dragonmonk111/junoclaw/commit/a7886cd
