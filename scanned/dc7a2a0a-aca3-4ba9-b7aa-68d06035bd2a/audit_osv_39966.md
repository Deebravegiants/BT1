# [H] Warp: Linux external editor command injection

## Summary
Severity: High
Advisory: CVE-2026-48731
Aliases: GHSA-7xgc-mhc8-g7wc
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48731
Type: osv

## Details
Warp is an agentic development environment. From 0.2024.02.20.08.01.stable_01 until 0.2026.05.06.15.42.stable_01, Warp contains a command injection issue in the Linux external editor launcher. Warp expanded freedesktop .desktop Exec templates for affected editor integrations and executed the expanded command through a shell. A user who opens an attacker-controlled local file path through an affected external editor or system-default editor route can cause shell syntax embedded in that path to execute as the local user. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48731.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-7xgc-mhc8-g7wc
- https://nvd.nist.gov/vuln/detail/CVE-2026-48731
- https://github.com/warpdotdev/warp/commit/861dacea2683f2fe263c3c3a1381c3cbb2b66809
