# [M] OpenClaw: `/phone arm`/`/phone disarm` Bypasses `operator.admin` Scope Check for External Channels 

## Summary
Severity: Medium
Advisory: GHSA-h2v7-xc88-xx8c
CVE: CVE-2026-41375
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-h2v7-xc88-xx8c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary
`/phone arm`/`/phone disarm` Bypasses `operator.admin` Scope Check for External Channels

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: Maintainers accepted this issue, fixed it in aa66ae1fc797d3298cc409ed2c5da69a89950a45 on 2026-03-27, and that fix shipped in v2026.3.28, so normalize it as a fixed released draft rather than a close-by-trust-model call.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.24`
- Patched versions: `>= 2026.3.28`
- First stable tag containing the fix: `v2026.3.28`

## Fix Commit(s)
- `aa66ae1fc797d3298cc409ed2c5da69a89950a45` — 2026-03-27T20:35:42Z

## Release Process Note
- The fix is already present in released version `2026.3.28`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h2v7-xc88-xx8c
- https://github.com/openclaw/openclaw
