# [H] OpenClaw: macOS Tailnet DNS Spoofing & Credential Exfiltration

## Summary
Severity: High
Advisory: GHSA-q9w8-cf67-r238
CVE: CVE-2026-41393
CWE: CWE-346, CWE-350
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-q9w8-cf67-r238
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
macOS Wide-Area Discovery Accepts Arbitrary Tailnet Peer as DNS Authority and Exfiltrates Operator Credentials

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Real shipped macOS discovery steering bug, but exploitation needs same-tailnet position, a CA-trusted endpoint, and user selection, so medium not high.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `a23c33a681f8c1b22dc793995acc4c5c4b568346` — 2026-03-31T10:04:11+01:00

OpenClaw thanks @nexrin for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q9w8-cf67-r238
- https://github.com/openclaw/openclaw/commit/a23c33a681f8c1b22dc793995acc4c5c4b568346
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
