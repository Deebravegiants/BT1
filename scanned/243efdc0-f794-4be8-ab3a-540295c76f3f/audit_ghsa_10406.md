# [M] OpenClaw: Discord voice manager bypasses channel-level member access allowlist

## Summary
Severity: Medium
Advisory: GHSA-cqgw-44wg-44rf
CVE: CVE-2026-41381
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-cqgw-44wg-44rf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Discord voice manager bypasses channel-level member access allowlist

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: v2026.3.28 still accepts Discord voice ingress before channel allowlist authorization, and main-only gating means this remains a real shipped access-control bug.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `dba96e7507e0900f120e5e28e57755d69bf78759` — 2026-03-31T21:29:13+09:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @zsxsoft for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cqgw-44wg-44rf
- https://github.com/openclaw/openclaw/commit/dba96e7507e0900f120e5e28e57755d69bf78759
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
