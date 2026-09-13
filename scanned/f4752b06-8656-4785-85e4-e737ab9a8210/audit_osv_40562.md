# [C] Termix: Missing authorization in SSH host credential resolution exposes stored credentials

## Summary
Severity: Critical
Advisory: CVE-2026-53546
Aliases: GHSA-57gp-39c7-4g9r
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-53546
Type: osv

## Details
Termix is a web-based server management platform with SSH terminal, tunneling, and file editing capabilities. Prior to 2.3.2, the terminal WebSocket accepts a user-controlled hostConfig.id and src/backend/ssh/host-resolver.ts resolves that host without requiring ownership or explicit access. When no credential is shared with the requester, resolveHostById performs an owner credential fallback, and src/backend/ssh/terminal.ts combines that credential with attacker-controlled ip, port, and username values. An authenticated low-privileged user can therefore make Termix authenticate to an attacker-controlled SSH server and disclose another user's stored SSH password or private-key material while the victim user's data key is unlocked. This issue is fixed in version 2.3.2.

## References
- https://github.com/Termix-SSH/Termix/releases/tag/release-2.3.2-tag
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53546.json
- https://github.com/Termix-SSH/Termix/security/advisories/GHSA-57gp-39c7-4g9r
- https://nvd.nist.gov/vuln/detail/CVE-2026-53546
- https://github.com/Termix-SSH/Termix/commit/52f4e51ae03b5b8d2608e1383e2ccf79d290132b
- https://github.com/Termix-SSH/Termix/pull/874
