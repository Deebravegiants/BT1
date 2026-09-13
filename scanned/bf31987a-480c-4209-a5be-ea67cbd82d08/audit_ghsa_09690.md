# [M] OpenClaw: /allowlist omits owner-only enforcement for cross-channel allowlist writes

## Summary
Severity: Medium
Advisory: GHSA-vc32-h5mq-453v
CVE: CVE-2026-41910
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-vc32-h5mq-453v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

/allowlist omits owner-only enforcement for cross-channel allowlist writes.

An authorized non-owner sender could attempt allowlist writes against a different channel.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<=v2026.4.1`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @zsxsoft and @KeenSecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vc32-h5mq-453v
- https://nvd.nist.gov/vuln/detail/CVE-2026-41910
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-owner-only-enforcement-in-allowlist-cross-channel-writes
