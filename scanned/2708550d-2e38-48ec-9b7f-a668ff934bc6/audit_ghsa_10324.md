# [M] OpenClaw: Image pixel-limit guard can fail open on sips and allow decompression-bomb DoS

## Summary
Severity: Medium
Advisory: GHSA-w85g-3h6x-4xh2
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-w85g-3h6x-4xh2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Image pixel-limit guard can fail open on sips and allow decompression-bomb DoS

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: Shipped v2026.3.28 image processing could fail open on oversized pixel counts and allow decompression-bomb DoS, an availability issue that is valid at medium.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `0ed4f8a72bb140045962e97ab01c94c076b758a4` — 2026-03-31T22:52:55+09:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w85g-3h6x-4xh2
- https://github.com/openclaw/openclaw/commit/0ed4f8a72bb140045962e97ab01c94c076b758a4
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
