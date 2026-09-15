# [H] OpenClaw: Gateway operator.write Can Reach Admin-Class Telegram Config and Cron Persistence via send

## Summary
Severity: High
Advisory: GHSA-767m-xrhc-fxm7
CVE: CVE-2026-41359
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-767m-xrhc-fxm7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary
Gateway operator.write Can Reach Admin-Class Telegram Config and Cron Persistence via send

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Real shipped operator.write to admin-class Telegram config or cron persistence bug, but it is an authenticated sink-specific escalation and high is too high given the narrower scope.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.24`
- Patched versions: `>= 2026.3.28`
- First stable tag containing the fix: `v2026.3.28`

## Fix Commit(s)
- `b7d70ade3b9900dbe97bd73be9c02e924ff3c986` — 2026-03-25T12:12:09-06:00

## Release Process Note
- The fix is already present in released version `2026.3.28`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-767m-xrhc-fxm7
- https://nvd.nist.gov/vuln/detail/CVE-2026-41359
- https://github.com/openclaw/openclaw/commit/b7d70ade3b9900dbe97bd73be9c02e924ff3c986
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-operator-write-to-admin-class-telegram-config-and-cron-persistence
