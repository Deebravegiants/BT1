# [H] Warp: Remote SSH cwd can lead to unauthorized remote command execution

## Summary
Severity: High
Advisory: CVE-2026-48732
Aliases: GHSA-qqpc-wvvw-4269
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48732
Type: osv

## Details
Warp is an agentic development environment. From 0.2023.03.21.08.02.stable_00 until 0.2026.05.06.15.42.stable_01, Warp contains a command injection issue in the legacy SSH background command path. Warp used the remote working directory reported by the session when building helper commands for SSH-backed metadata collection. A remote host, repository, or directory name controlled by an attacker could cause that helper command to execute additional shell syntax on the remote host as the victim's authenticated SSH account. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48732.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-qqpc-wvvw-4269
- https://nvd.nist.gov/vuln/detail/CVE-2026-48732
- https://github.com/warpdotdev/warp/commit/88c344e2de662a935f0ef0896458494ef2413add
