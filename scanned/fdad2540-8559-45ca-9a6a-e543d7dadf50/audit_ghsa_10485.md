# [H] OpenClaw: Node browser proxy `allowProfiles` bypass through persistent profile mutation and runtime profile selection

## Summary
Severity: High
Advisory: GHSA-h5hg-h7rr-gpf3
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-h5hg-h7rr-gpf3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Node browser proxy `allowProfiles` bypass through persistent profile mutation and runtime profile selection

## Current Maintainer Triage
- Status: open
- Normalized severity: high
- Assessment: Real released allowProfiles bypass through profile mutation and runtime profile selection, fixed and shipped in v2026.3.22+, so keep open for publish rather than close.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.13-1`
- Patched versions: `>= 2026.3.22`
- First stable tag containing the fix: `v2026.3.22`

## Fix Commit(s)
- `eac93507c36ccd0c359fba18fa466ef6448be8a5` — 2026-03-23T00:56:44-07:00

## Release Process Note
- The fix is already present in released version `2026.3.22`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h5hg-h7rr-gpf3
- https://github.com/openclaw/openclaw/commit/eac93507c36ccd0c359fba18fa466ef6448be8a5
- https://github.com/openclaw/openclaw
