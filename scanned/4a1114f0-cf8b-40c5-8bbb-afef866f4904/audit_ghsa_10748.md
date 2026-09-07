# [C] OpenClaw: Heartbeat context inheritance bypasses sandbox via senderIsOwner escalation

## Summary
Severity: Critical
Advisory: GHSA-g5cg-8x5w-7jpm
CVE: CVE-2026-41329
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-g5cg-8x5w-7jpm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Heartbeat context inheritance bypasses sandbox via senderIsOwner escalation

## Current Maintainer Triage
- Status: open
- Normalized severity: Critical

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `a30214a624946fc5c85c9558a27c1580172374fd` — 2026-03-31T09:06:51+09:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g5cg-8x5w-7jpm
- https://github.com/openclaw/openclaw/commit/a30214a624946fc5c85c9558a27c1580172374fd
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
