# [M] OpenClaw: Strict browser SSRF bypass in Playwright redirect handling leaves private targets reachable

## Summary
Severity: Medium
Advisory: GHSA-w8g9-x8gx-crmm
CVE: CVE-2026-42430
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-w8g9-x8gx-crmm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.8

## Details
## Impact

Strict browser SSRF bypass in Playwright redirect handling leaves private targets reachable.

Strict browser SSRF checks could miss Playwright request-time navigation to private targets.

OpenClaw is a user-controlled local assistant. This advisory is scoped to the OpenClaw trust model and does not assume a multi-tenant service boundary.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `2026.3.8`
- Patched versions: `2026.4.8`

## Fix

The issue was fixed on `main` and is available in the patched npm version listed above. The verified fixed tree is commit `d7c3210cd6f5fdfdc1beff4c9541673e814354d5`.

## Verification

The fix was re-checked against `main` before publication, including targeted regression tests for the affected security boundary.

## Credits

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w8g9-x8gx-crmm
- https://nvd.nist.gov/vuln/detail/CVE-2026-42430
- https://github.com/openclaw/openclaw/commit/d7c3210cd6f5fdfdc1beff4c9541673e814354d5
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-strict-browser-ssrf-bypass-via-playwright-redirect-handling
