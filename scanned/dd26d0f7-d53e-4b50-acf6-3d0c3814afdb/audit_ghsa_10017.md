# [M] OpenClaw: Shared reply MEDIA - paths are treated as trusted and can trigger cross-channel local file exfiltration

## Summary
Severity: Medium
Advisory: GHSA-qqq7-4hxc-x63c
CVE: CVE-2026-42424
CWE: CWE-668, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-qqq7-4hxc-x63c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

Shared reply MEDIA: paths are treated as trusted and can trigger cross-channel local file exfiltration.

A crafted shared reply MEDIA reference could cause another channel to read a local file path as trusted generated media.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<=2026.4.4`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @threalwinky for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qqq7-4hxc-x63c
- https://nvd.nist.gov/vuln/detail/CVE-2026-42424
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-local-file-exfiltration-via-shared-reply-media-paths
