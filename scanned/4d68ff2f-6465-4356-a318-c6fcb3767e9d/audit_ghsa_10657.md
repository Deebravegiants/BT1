# [M] OpenClaw has Browser SSRF Policy Bypass via Interaction-Triggered Navigation

## Summary
Severity: Medium
Advisory: GHSA-vr5g-mmx7-h897
CVE: CVE-2026-41912
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-vr5g-mmx7-h897
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

Browser SSRF Policy Bypass via Interaction-Triggered Navigation.

Browser interactions could trigger navigations that bypassed the normal SSRF navigation checks.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.5`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @ccreater222 and @KeenSecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vr5g-mmx7-h897
- https://github.com/openclaw/openclaw
