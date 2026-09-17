# [M] OpenClaw: `session_status` still bypasses configured `tools.sessions.visibility` for unsandboxed invocations 

## Summary
Severity: Medium
Advisory: GHSA-fwjq-xwfj-gv75
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-fwjq-xwfj-gv75
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
`session_status` still bypasses configured `tools.sessions.visibility` for unsandboxed invocations

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Real on shipped v2026.3.22: non-sandboxed session_status skipped the shared visibility guard, but this is a same-agent session-policy bypass with unreleased fix, not a broader host-boundary break.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `4d369a3400dc9b737fbe8daa63f09d909ce7beb8` — 2026-03-30T16:48:12+02:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fwjq-xwfj-gv75
- https://github.com/openclaw/openclaw/commit/4d369a3400dc9b737fbe8daa63f09d909ce7beb8
- https://github.com/openclaw/openclaw
