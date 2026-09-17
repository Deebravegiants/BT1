# [H] OpenClaw's Windows cmd.exe parsing may bypass exec allowlist/approval gating

## Summary
Severity: High
Advisory: GHSA-qj77-c3c8-9c3q
CVE: CVE-2026-28391
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-qj77-c3c8-9c3q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.2

## Details
### Summary

On Windows nodes, exec requests were executed via `cmd.exe /d /s /c <rawCommand>`. In allowlist/approval-gated mode, the allowlist analysis did not model Windows `cmd.exe` parsing and metacharacter behavior. A crafted command string could cause `cmd.exe` to interpret additional operations (for example command chaining via `&`, or expansion via `%...%` / `!...!`) beyond what was allowlisted/approved.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.1`
- Patched: `>= 2026.2.2`
- Latest (npm) as of 2026-02-14: `2026.2.13`

### Details

- Default installs: Not affected unless you opt into exec allowlist/approval gating on Windows nodes.
- Windows execution uses `cmd.exe` via `src/infra/node-shell.ts`.
- The fix hardens Windows allowlist enforcement by:
  - Passing the platform into allowlist analysis and rejecting Windows shell metacharacters.
  - Treating `cmd.exe` invocation as not allowlist-safe on Windows.
  - Avoiding `cmd.exe` entirely in allowlist mode by executing the parsed argv directly when possible.

### Fix Commit(s)

- `a7f4a53ce80c98ba1452eb90802d447fca9bf3d6`

Thanks @simecek for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qj77-c3c8-9c3q
- https://nvd.nist.gov/vuln/detail/CVE-2026-28391
- https://github.com/openclaw/openclaw/commit/a7f4a53ce80c98ba1452eb90802d447fca9bf3d6
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.2
- https://www.vulncheck.com/advisories/openclaw-command-injection-via-cmdexe-parsing-bypass-in-allowlist-enforcement
