# [M] OpenClaw B-M3: ClawHub package downloads are not enforced with integrity verification

## Summary
Severity: Medium
Advisory: GHSA-3vvq-q2qc-7rmp
CVE: CVE-2026-42428
CWE: CWE-353
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-3vvq-q2qc-7rmp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

B-M3: ClawHub package downloads are not enforced with integrity verification.

ClawHub downloads could install plugin archives without enforcing archive or per-file integrity metadata.

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
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3vvq-q2qc-7rmp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42428
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-missing-integrity-verification-in-package-downloads
