# [H] OpenClaw Has Incomplete Fix for CVE-2026-4039: CLI Backend Environment Variable Injection via Workspace Config

## Summary
Severity: High
Advisory: GHSA-vfw7-6rhc-6xxg
CVE: CVE-2026-41384
CWE: CWE-15, CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-vfw7-6rhc-6xxg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.24

## Details
## Summary
Incomplete Fix for CVE-2026-4039: CLI Backend Environment Variable Injection via Workspace Config

## Current Maintainer Triage
- Status: open
- Normalized severity: high
- Assessment: Real shipped malicious-workspace-config env injection in the CLI backend runner, fixed by sanitizing backend env before spawn and shipped in v2026.3.24, so advisory stays open until published.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.23-2`
- Patched versions: `>= 2026.3.24`
- First stable tag containing the fix: `v2026.3.24`

## Fix Commit(s)
- `c2fb7f1948c3226732a630256b5179a60664ec24` — 2026-03-24T12:58:10-07:00

## Release Process Note
- The fix is already present in released version `2026.3.24`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @YLChen-007 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vfw7-6rhc-6xxg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41384
- https://github.com/openclaw/openclaw/commit/c2fb7f1948c3226732a630256b5179a60664ec24
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-environment-variable-injection-via-workspace-config-in-cli-backend
