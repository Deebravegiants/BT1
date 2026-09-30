# [H] Warp: Command Injection via Warp code search tool arguments

## Summary
Severity: High
Advisory: CVE-2026-48703
Aliases: GHSA-8r78-7jwh-m6hm
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48703
Type: osv

## Details
Warp is an agentic development environment. From 0.2025.04.09.08.11.stable_00 until 0.2026.05.06.15.42.stable_01, Warp contains a command execution policy bypass in Agent code search tools. The affected Grep and FileGlob actions are authorized as read/search operations, but their implementations build shell command strings from Agent-controlled inputs (search text, paths, glob patterns) and execute them in the active terminal session. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48703.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-8r78-7jwh-m6hm
- https://nvd.nist.gov/vuln/detail/CVE-2026-48703
- https://github.com/warpdotdev/warp/commit/43f4f483e0c2dd253d2aaa8a495b2d71f0208c40
