# [H] OpenClaw has macOS `system.run` allowlist bypass via quoted command substitution

## Summary
Severity: High
Advisory: GHSA-9p38-94jf-hgjj
CVE: CVE-2026-22179
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-9p38-94jf-hgjj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
In OpenClaw's macOS node-host path, `system.run` allowlist parsing in `security=allowlist` mode failed to reject command substitution tokens when they appeared inside double-quoted shell text.

Because of that gap, payloads like `echo "ok $(id)"` could be treated as allowlist hits (first executable token `echo`) while still executing non-allowlisted subcommands through shell substitution.

### Affected Packages / Versions
- Package: npm `openclaw`
- Latest published affected version: `2026.2.21-2`
- Affected range: `<= 2026.2.21-2`
- Patched version (planned next release): `2026.2.22`

Notes:
- Default installs are not affected (`security=deny` by default).
- The issue requires opting into `security=allowlist` on the macOS node-host path.

### Impact
Approval/authorization bypass in allowlist mode that can lead to unintended command execution on the node host.

### Preconditions
- Target uses macOS node-host / companion-app execution path.
- Exec approvals set to `security=allowlist`.
- Ask mode is `on-miss` or `off`.
- Allowlist contains a benign executable used in a shell wrapper flow (for example `/bin/echo`).

### Reproduction (example)
Use a shell-wrapper command where the visible executable is allowlisted but the quoted payload contains substitution:

- command argv: `/bin/sh -lc 'echo "ok $(/usr/bin/id > /tmp/openclaw-poc-rce)"'`
- allowlist pattern includes `/bin/echo`

Before the fix, allowlist analysis could resolve this as allowlisted while shell substitution still executed.

### Remediation
- Upgrade to `2026.2.22` (or newer) when released.
- Temporary mitigation: set ask mode to `always` or set security mode to `deny`.

### Fix Commit(s)
- `90a378ca3a9ecbf1634cd247f17a35f4612c6ca6`

### Release Process Note
`patched_versions` is pre-set to planned next release `2026.2.22`. After npm release is out, advisory can be published directly.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9p38-94jf-hgjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-22179
- https://github.com/openclaw/openclaw/commit/90a378ca3a9ecbf1634cd247f17a35f4612c6ca6
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-command-substitution-in-system-run
