# [M] OpenClaw: Path traversal via inbound channel attachment path in ACP dispatch allows arbitrary file read

## Summary
Severity: Medium
Advisory: GHSA-58q2-7r52-jq62
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-58q2-7r52-jq62
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Path traversal via inbound channel attachment path in ACP dispatch allows arbitrary file read

## Current Maintainer Triage
- Normalized severity: medium
- Assessment: v2026.3.28 ACP dispatch still reads attachment paths outside the guarded attachment-cache or root checks, and the root-enforcement fix is not yet shipped.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `566fb73d9da2d73c0be0d9b8e5b762e4dcd8e81d` — 2026-03-30T14:04:02+01:00

OpenClaw thanks @north-echo for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-58q2-7r52-jq62
- https://github.com/openclaw/openclaw/commit/566fb73d9da2d73c0be0d9b8e5b762e4dcd8e81d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
