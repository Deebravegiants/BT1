# [H] Warp: Env-var prefixes can lead to denylisted command autoexecution

## Summary
Severity: High
Advisory: CVE-2026-48721
Aliases: GHSA-3839-h8jj-ph82
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48721
Type: osv

## Details
Warp is an agentic development environment. From 0.2025.10.08.08.12.stable_00 until 0.2026.05.06.15.42.stable_01, Warp contains a command execution permission-check bypass in the default unsandboxed CLI agent profile. The CLI profile is non-interactive and relies on a command denylist as a safety boundary for commands that should require confirmation. Because command strings were checked before canonicalizing leading environment-variable assignments, an attacker who can influence the agent's command output may cause denylisted commands to be treated as non-denylisted. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48721.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-3839-h8jj-ph82
- https://nvd.nist.gov/vuln/detail/CVE-2026-48721
- https://github.com/warpdotdev/warp/commit/0c1e243292c642d9a7748f80813b6fdfc0b31a9e
