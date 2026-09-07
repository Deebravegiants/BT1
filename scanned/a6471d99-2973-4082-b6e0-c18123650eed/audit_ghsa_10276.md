# [C] OpenClaw: Sandbox escape via TOCTOU race in remote FS bridge readFile

## Summary
Severity: Critical
Advisory: GHSA-9p3r-hh9g-5cmg
CVE: CVE-2026-41296
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-9p3r-hh9g-5cmg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Sandbox escape via TOCTOU race in remote FS bridge readFile

## Current Maintainer Triage
- Normalized severity: critical
- Assessment: v2026.3.28 remote sandbox reads still do path-check then separate file read, so the TOCTOU sandbox escape remains present in the latest shipped tag.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `121870a08583033ed6a0ed73d9ffea32991252bb` — 2026-03-31T09:55:51+09:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9p3r-hh9g-5cmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41296
- https://github.com/openclaw/openclaw/commit/121870a08583033ed6a0ed73d9ffea32991252bb
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-sandbox-escape-via-toctou-race-in-remote-fs-bridge-readfile
