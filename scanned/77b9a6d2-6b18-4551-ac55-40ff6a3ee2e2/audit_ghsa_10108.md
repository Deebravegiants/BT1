# [M] OpenClaw runs Discord audio preflight transcription before member authorization

## Summary
Severity: Medium
Advisory: GHSA-hhff-fj5f-qg48
CVE: CVE-2026-41374
CWE: CWE-408, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-hhff-fj5f-qg48
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Discord audio preflight transcription before member authorization

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: v2026.3.28 still runs Discord audio preflight before member allowlist rejection, but this is the same pre-auth resource-consumption class and not the high-severity auth-bypass framing in the draft.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `ee52f64226a03efadfdf1e3b759e13424a3d4e41` — 2026-03-30T14:38:22+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hhff-fj5f-qg48
- https://nvd.nist.gov/vuln/detail/CVE-2026-41374
- https://github.com/openclaw/openclaw/commit/ee52f64226a03efadfdf1e3b759e13424a3d4e41
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-resource-consumption-via-discord-audio-preflight-before-member-authorization
