# [H] OpenClaw: Incomplete scope-clearing fix allows operator.admin escalation via trusted-proxy auth mode

## Summary
Severity: High
Advisory: GHSA-g374-mggx-p6xc
CVE: CVE-2026-41404
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-g374-mggx-p6xc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Incomplete scope-clearing fix allows operator.admin escalation via trusted-proxy auth mode

## Current Maintainer Triage
- Normalized severity: high
- Assessment: v2026.3.28 still misses trusted-proxy scope clearing for non-Control-UI clients, so self-declared operator scopes can survive on a real identity-bearing auth path; the complete fix is unreleased.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `8b88b927cb0747ad24d95b07d35682bf85dc5b0e` — 2026-03-30T14:19:00+01:00

OpenClaw thanks @north-echo for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g374-mggx-p6xc
- https://github.com/openclaw/openclaw/commit/8b88b927cb0747ad24d95b07d35682bf85dc5b0e
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
