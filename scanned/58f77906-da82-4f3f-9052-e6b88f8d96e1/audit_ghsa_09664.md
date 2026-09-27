# [H] OpenClaw: `fetchWithSsrFGuard` replays unsafe request bodies across cross-origin redirects

## Summary
Severity: High
Advisory: GHSA-qx8j-g322-qj6m
CVE: CVE-2026-40037
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-qx8j-g322-qj6m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

`fetchWithSsrFGuard` replays unsafe request bodies across cross-origin redirects.

A guarded fetch could resend unsafe request bodies or headers when following cross-origin redirects.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<2026.3.31`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @BG0ECV for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qx8j-g322-qj6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-40037
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unsafe-request-body-replay-via-fetchwithssrfguard-cross-origin-redirects
