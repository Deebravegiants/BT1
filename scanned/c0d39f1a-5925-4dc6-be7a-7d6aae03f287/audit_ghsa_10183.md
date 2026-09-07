# [H] OpenClaw: MS Teams webhook parses body before JWT validation, enabling unauthenticated resource exhaustion

## Summary
Severity: High
Advisory: GHSA-p464-m8x6-vhv8
CVE: CVE-2026-41405
CWE: CWE-400, CWE-408
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-p464-m8x6-vhv8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
MS Teams webhook parses body before JWT validation, enabling unauthenticated resource exhaustion

## Current Maintainer Triage
- Status: open
- Normalized severity: medium
- Assessment: v2026.3.28 still parses Teams JSON after only a Bearer-prefix gate and before real JWT validation, and the auth-before-parse fix is not yet shipped.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `3834d47099dd13c8244ed6de8b9ea9855c553623` — 2026-03-30T13:46:40+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p464-m8x6-vhv8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41405
- https://github.com/openclaw/openclaw/commit/3834d47099dd13c8244ed6de8b9ea9855c553623
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-resource-exhaustion-via-unauthenticated-ms-teams-webhook-body-parsing
