# [M] OpenClaw: strictInlineEval explicit-approval boundary bypassed by approval-timeout fallback on gateway and node exec hosts

## Summary
Severity: Medium
Advisory: GHSA-q2gc-xjqw-qp89
CVE: CVE-2026-42423
CWE: CWE-20, CWE-636
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-q2gc-xjqw-qp89
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

strictInlineEval explicit-approval boundary bypassed by approval-timeout fallback on gateway and node exec hosts.

The approval-timeout fallback could allow inline eval commands that strictInlineEval was meant to require explicit approval for.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<=2026.4.2`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @zsxsoft and @KeenSecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q2gc-xjqw-qp89
- https://nvd.nist.gov/vuln/detail/CVE-2026-42423
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-strictinlineeval-approval-boundary-bypass-via-approval-timeout-fallback
