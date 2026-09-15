# [M] OpenClaw: Gateway operator.write Can Reach Admin-Class Talk Voice Config Persistence via chat.send

## Summary
Severity: Medium
Advisory: GHSA-3q42-xmxv-9vfr
CVE: CVE-2026-41379
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-3q42-xmxv-9vfr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary
Gateway operator.write Can Reach Admin-Class Talk Voice Config Persistence via chat.send

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Real shipped operator.write to admin-class Talk Voice config persistence bug, but it is the same narrow authenticated persistence class and should be normalized below high.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.24`
- Patched versions: `>= 2026.3.28`
- First stable tag containing the fix: `v2026.3.28`

## Fix Commit(s)
- `e34694733fc64931ed4a543c73d84ad3435d5df1` — 2026-03-25T19:55:26Z

## Release Process Note
- The fix is already present in released version `2026.3.28`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3q42-xmxv-9vfr
- https://github.com/openclaw/openclaw/commit/e34694733fc64931ed4a543c73d84ad3435d5df1
- https://github.com/openclaw/openclaw
