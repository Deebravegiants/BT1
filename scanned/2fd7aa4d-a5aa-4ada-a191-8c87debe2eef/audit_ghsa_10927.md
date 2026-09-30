# [M] OpenClaw's system.run allowlist bypass via shell line-continuation command substitution

## Summary
Severity: Medium
Advisory: GHSA-9868-vxmx-w862
CVE: CVE-2026-28460
CWE: CWE-78, CWE-863
Ecosystem: npm
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-9868-vxmx-w862
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
In OpenClaw `system.run` allowlist mode, shell-wrapper analysis could be bypassed by splitting command substitution as `$\\` + newline + `(` inside double quotes. Analysis treated the payload as allowlisted (for example `/bin/echo`), while shell runtime folded the line continuation into `$(...)` and executed non-allowlisted subcommands.

### Affected Packages / Versions
- Package: npm `openclaw`
- Latest published affected version: `2026.2.21-2`
- Affected range: `<=2026.2.21-2`
- Patched version (planned next release): `2026.2.22`

### Impact
In deployments that opt into `tools.exec.security=allowlist` (with `ask=on-miss` or `off`), this can bypass approval boundaries and lead to unintended command execution.

### Fix Commit(s)
- `3f0b9dbb36c86e308267924c0d3d4a4e1fc4d1e9`

### Remediation
- Upgrade to `2026.2.22` (or newer) when published.
- Temporary mitigation: set `tools.exec.ask=always` or `tools.exec.security=deny`.

### Release Process Note
`patched_versions` is pre-set to planned next release `2026.2.22`. After npm release is out, this advisory should be ready for direct publish without additional metadata edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9868-vxmx-w862
- https://nvd.nist.gov/vuln/detail/CVE-2026-28460
- https://github.com/openclaw/openclaw/commit/3f0b9dbb36c86e308267924c0d3d4a4e1fc4d1e9
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-shell-line-continuation-command-substitution-in-system-run
