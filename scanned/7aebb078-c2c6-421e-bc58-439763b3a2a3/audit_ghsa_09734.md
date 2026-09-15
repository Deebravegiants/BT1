# [M] OpenClaw: resolvedAuth closure becomes stale after config reload

## Summary
Severity: Medium
Advisory: GHSA-68x5-xx89-w9mm
CVE: CVE-2026-41916
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-68x5-xx89-w9mm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

resolvedAuth closure becomes stale after config reload.

After a config reload, newly accepted gateway connections could continue using stale resolved auth state.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @kexinoh of Tencent zhuque Lab (https://github.com/Tencent/AI-Infra-Guard) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-68x5-xx89-w9mm
- https://github.com/openclaw/openclaw
