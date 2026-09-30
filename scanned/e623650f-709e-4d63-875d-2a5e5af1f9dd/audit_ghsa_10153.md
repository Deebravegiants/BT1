# [M] OpenClaw: Multiple Code Paths Missing Base64 Pre-Allocation Size Checks

## Summary
Severity: Medium
Advisory: GHSA-ccx3-fw7q-rr2r
CVE: CVE-2026-42420
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-ccx3-fw7q-rr2r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

Multiple Code Paths Missing Base64 Pre-Allocation Size Checks.

Several base64 decode paths could allocate before enforcing decoded-size limits.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<=v2026.4.2`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @zsxsoft and @KeenSecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-ccx3-fw7q-rr2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42420
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-improper-base64-decoding-size-validation
