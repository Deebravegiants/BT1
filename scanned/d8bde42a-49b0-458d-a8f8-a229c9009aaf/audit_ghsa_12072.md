# [H] OpenClaw's tools.exec.safeBins sort long-option abbreviation bypass can skip exec approval in allowlist mode

## Summary
Severity: High
Advisory: GHSA-3c6h-g97w-fg78
CVE: CVE-2026-32059
CWE: CWE-184, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-3c6h-g97w-fg78
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
### Summary
In OpenClaw, `tools.exec.safeBins` validation for `sort` could be bypassed via GNU long-option abbreviations in allowlist mode, allowing approval-free execution paths that should require approval.

### Affected Packages / Versions
- Ecosystem: npm
- Package: `openclaw`
- Latest published version checked: `2026.2.22-2`
- Affected range: `<= 2026.2.22-2`
- Fixed version: `2026.2.23`

### Impact
When all of the following are true:
- `tools.exec.security=allowlist`
- `tools.exec.ask=on-miss`
- `tools.exec.safeBins` includes `sort`

abbreviated GNU long options (for example `--compress-prog`) could bypass denied-flag checks and be treated as allowlist-satisfied safe-bin usage, skipping approval.

### Root Cause
Long-option handling matched denied flags by exact string and accepted unknown long options with inline values instead of failing closed.

### Fix Commit(s)
- `3b8e33037ae2e12af7beb56fcf0346f1f8cbde6f`

### Release Process Note
`patched_versions` is pre-set to the released version (`2026.2.23`). This advisory now reflects released fix version `2026.2.23`.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3c6h-g97w-fg78
- https://nvd.nist.gov/vuln/detail/CVE-2026-32059
- https://github.com/openclaw/openclaw/commit/3b8e33037ae2e12af7beb56fcf0346f1f8cbde6f
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-sort-long-option-abbreviation-in-toolsexecsafebins
