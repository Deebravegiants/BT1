# [M] OpenClaw QQ Bot Extension missing SSRF Protection on All Media Fetch Paths

## Summary
Severity: Medium
Advisory: GHSA-3fv3-6p2v-gxwj
CVE: CVE-2026-41914
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-3fv3-6p2v-gxwj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

QQ Bot Extension: Missing SSRF Protection on All Media Fetch Paths.

QQ Bot media download paths were not consistently routed through the SSRF guard and allowlist policy.

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

Thanks @adithyan-ak for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3fv3-6p2v-gxwj
- https://github.com/openclaw/openclaw
