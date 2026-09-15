# [M] OpenClaw: Telegram legacy allowFrom migration fans default-account trust into all named accounts

## Summary
Severity: Medium
Advisory: GHSA-f693-58pc-2gfr
CWE: CWE-732
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-f693-58pc-2gfr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Telegram legacy allowFrom migration fans default-account trust into all named accounts

## Current Maintainer Triage
- Status: open
- Normalized severity: low
- Assessment: Shipped v2026.3.28 Telegram migration fans legacy default-account allowFrom trust into named accounts, which is an in-scope auth-boundary bug and low fits.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `d8c68c8d4265ea6fa5e8c5e056534c351bddef37` — 2026-03-31T12:51:38+01:00

## Release Process Note
- The fix is already present in released version `2026.3.31`.
- This draft looks ready for final maintainer disposition or publication, not additional code-fix work.

Thanks @smaeljaish771 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f693-58pc-2gfr
- https://github.com/openclaw/openclaw/commit/d8c68c8d4265ea6fa5e8c5e056534c351bddef37
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
