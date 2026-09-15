# [M] OpenClaw Host-Exec Environment Variable Injection

## Summary
Severity: Medium
Advisory: GHSA-w9j9-w4cp-6wgr
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-w9j9-w4cp-6wgr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

OpenClaw Host-Exec Environment Variable Injection.

Host exec could inherit environment variables that influence interpreters, shells, or build tools.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.28`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @wsparks-vc for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w9j9-w4cp-6wgr
- https://github.com/openclaw/openclaw
