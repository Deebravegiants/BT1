# [M] OpenClaw: Media download follows cross-origin redirects with Authorization headers intact

## Summary
Severity: Medium
Advisory: GHSA-68v4-hmwv-f43h
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-68v4-hmwv-f43h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Media download follows cross-origin redirects with Authorization headers intact

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: Shipped v2026.3.28 media downloads forwarded Authorization across cross-origin redirects, a real in-scope credential-leak class that fits medium.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `e704323ff388ed21f6963f9b8e0b1b8dfaaabc5f` — 2026-03-31T19:57:42+09:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-68v4-hmwv-f43h
- https://github.com/openclaw/openclaw/commit/e704323ff388ed21f6963f9b8e0b1b8dfaaabc5f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
