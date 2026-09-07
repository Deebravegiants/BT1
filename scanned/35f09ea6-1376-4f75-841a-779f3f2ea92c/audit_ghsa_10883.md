# [H] OpenClaw's Telegram message_reaction authorization bypass allows unauthorized system-event injection

## Summary
Severity: High
Advisory: GHSA-qj22-xqjr-v83v
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-qj22-xqjr-v83v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
A missing sender-authorization check in Telegram `message_reaction` handling allowed unauthorized users to trigger reaction-derived system events.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Introduced: `2026.2.17`
- Affected: `>= 2026.2.17` and `<= 2026.2.24`
- Latest published at patch time: `2026.2.24`
- Patched in release: `2026.2.25`

## Impact

When reaction notifications are enabled, unauthorized Telegram senders could inject reaction system events despite configured DM/group authorization controls (`dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`).

## Fix Commit(s)

- `e56b0cf1a04f992ac6ebc775899f48ea31687640`

## Release Process Note

`patched_versions` is pre-set to the release (`2026.2.25`) so once npm release `2026.2.25` is published, this advisory can be published without further edits.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qj22-xqjr-v83v
- https://github.com/openclaw/openclaw/commit/e56b0cf1a04f992ac6ebc775899f48ea31687640
- https://github.com/openclaw/openclaw
