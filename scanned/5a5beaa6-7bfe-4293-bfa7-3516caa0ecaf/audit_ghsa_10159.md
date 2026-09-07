# [M] OpenClaw: Telegram audio preflight transcription enables resource consumption by unauthorized senders

## Summary
Severity: Medium
Advisory: GHSA-m6fx-m8hc-572m
CVE: CVE-2026-41331
CWE: CWE-408, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-m6fx-m8hc-572m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Telegram audio preflight transcription enables resource consumption by unauthorized senders

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: v2026.3.28 still lets unauthorized Telegram group senders trigger audio preflight before allowlist enforcement, but the real impact is resource or billing burn rather than direct data exposure or host compromise.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `c4fa8635d03943ffe9e294d501089521dca635c5` — 2026-03-30T12:19:31+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-m6fx-m8hc-572m
- https://nvd.nist.gov/vuln/detail/CVE-2026-41331
- https://github.com/openclaw/openclaw/commit/c4fa8635d03943ffe9e294d501089521dca635c5
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-resource-consumption-via-unauthorized-telegram-audio-preflight-transcription
