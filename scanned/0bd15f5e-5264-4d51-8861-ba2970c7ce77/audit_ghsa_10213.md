# [M] OpenClaw: Marketplace Plugin Download Follows Redirects Without SSRF Protection

## Summary
Severity: Medium
Advisory: GHSA-vjx8-8p7h-82gr
CVE: CVE-2026-41297
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-vjx8-8p7h-82gr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Marketplace Plugin Download Follows Redirects Without SSRF Protection

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: v2026.3.28 still uses bare redirect-following fetch in src/plugins/marketplace.ts for marketplace archives, and fixed-on-main only does not change that shipped SSRF exposure.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `2ce44ca6a1302b166a128abbd78f72114f2f4f52` — 2026-03-31T12:59:42+01:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vjx8-8p7h-82gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41297
- https://github.com/openclaw/openclaw/commit/2ce44ca6a1302b166a128abbd78f72114f2f4f52
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-via-marketplace-plugin-download-redirect
