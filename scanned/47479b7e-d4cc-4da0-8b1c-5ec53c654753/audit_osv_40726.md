# [M] Warp: DCS lifecycle hook spoofing can alter terminal session metadata

## Summary
Severity: Medium
Advisory: CVE-2026-54686
Aliases: GHSA-9w2v-jhww-vm85
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-54686
Type: osv

## Details
Warp is an agentic development environment. From 0.2021.04.25.23.05.stable_00 until 0.2026.05.06.15.42.stable_01, Warp accepted certain state-mutating terminal lifecycle hooks from the PTY stream without verifying that the hooks were emitted by Warp's shell integration for the active session. An attacker who could cause a victim to view attacker-controlled terminal output in Warp could spoof selected lifecycle metadata, including the current working directory reported for the active block or SSH session transport metadata. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54686.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-9w2v-jhww-vm85
- https://nvd.nist.gov/vuln/detail/CVE-2026-54686
- https://github.com/warpdotdev/warp/commit/32d21d15c9a3da1a923d1ed66226cf5cba081d16
- https://github.com/warpdotdev/warp/commit/51bd3267803c5cc0a45074fa19fd50162be7c917
