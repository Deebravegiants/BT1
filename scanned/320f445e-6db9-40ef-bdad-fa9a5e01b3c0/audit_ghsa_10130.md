# [M] OpenClaw: Tlon media downloads can bypass core safety limits and exhaust disk

## Summary
Severity: Medium
Advisory: GHSA-4g5x-2jfc-xm98
CVE: CVE-2026-41408
CWE: CWE-434, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-4g5x-2jfc-xm98
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Tlon media downloads can bypass core safety limits and exhaust disk

## Current Maintainer Triage
- Status: narrow
- Normalized severity: low
- Assessment: Shipped v2026.3.28 Tlon media downloads bypassed core size/count/cleanup limits, but this is availability-only resource exhaustion in a bundled plugin path, so low.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `2194587d70d2aef863508b945319c5a7c88b12ce` — 2026-03-31T19:40:15+09:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4g5x-2jfc-xm98
- https://nvd.nist.gov/vuln/detail/CVE-2026-41408
- https://github.com/openclaw/openclaw/commit/2194587d70d2aef863508b945319c5a7c88b12ce
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-disk-exhaustion-via-media-download-bypass
