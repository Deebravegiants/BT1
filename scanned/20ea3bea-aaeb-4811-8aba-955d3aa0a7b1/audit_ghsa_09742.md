# [M] OpenClaw: Endpoint persists after trust decline, leaking gateway credentials

## Summary
Severity: Medium
Advisory: GHSA-9f4w-67g7-mqwv
CVE: CVE-2026-41300
CWE: CWE-670
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-9f4w-67g7-mqwv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Remote onboarding preserves attacker-discovered endpoint after trust decline, routing gateway credentials to it

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Real shipped onboarding trust-decline bug because the declined discovered URL survived into the manual prompt, but operator acceptance of that prefill is still required, so medium.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `2a75416634837c21ed05b8c3ed906eb7a7807060` — 2026-03-30T20:03:06+01:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @zsxsoft for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9f4w-67g7-mqwv
- https://github.com/openclaw/openclaw/commit/2a75416634837c21ed05b8c3ed906eb7a7807060
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
