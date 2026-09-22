# [H] OpenClaw: Authenticated `/hooks/wake` and mapped `wake` payloads are promoted into the trusted `System:` prompt channel

## Summary
Severity: High
Advisory: GHSA-jf56-mccx-5f3f
CWE: CWE-501
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-jf56-mccx-5f3f
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

Authenticated `/hooks/wake` and mapped `wake` payloads are promoted into the trusted `System:` prompt channel.

An authenticated wake hook or mapped wake payload could be promoted into the trusted System prompt channel instead of an untrusted event.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.2`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jf56-mccx-5f3f
- https://github.com/openclaw/openclaw
