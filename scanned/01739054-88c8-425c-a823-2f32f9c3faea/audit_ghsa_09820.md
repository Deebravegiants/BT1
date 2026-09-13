# [M] OpenClaw: Voice-call still parses large WebSocket frames before start validation (Incomplete fix for CVE-2026-32062)

## Summary
Severity: Medium
Advisory: GHSA-2w79-r9g8-wmcr
CVE: CVE-2026-41400
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-2w79-r9g8-wmcr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Incomplete fix for CVE-2026-32062: voice-call still parses large WebSocket frames before start validation

## Current Maintainer Triage
- Normalized severity: medium
- Assessment: v2026.3.28 still parses oversized pre-start voice-call WebSocket frames before start validation, and the unreleased maxPayload fix confirms the shipped resource-consumption bug remains open.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `9abcfdadf591bf266d85fbdfe14ae833e557a110` — 2026-03-31T19:47:10+09:00

OpenClaw thanks @Kazamayc for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2w79-r9g8-wmcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-41400
- https://github.com/openclaw/openclaw/commit/9abcfdadf591bf266d85fbdfe14ae833e557a110
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-resource-consumption-via-oversized-websocket-frames-in-voice-call
