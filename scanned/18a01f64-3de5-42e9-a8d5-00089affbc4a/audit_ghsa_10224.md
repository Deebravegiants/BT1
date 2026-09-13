# [H] OpenClaw: Host exec environment sanitization misses package, registry, Docker, compiler, and TLS override variables

## Summary
Severity: High
Advisory: GHSA-cg7q-fg22-4g98
CVE: CVE-2026-41369
CWE: CWE-184, CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-cg7q-fg22-4g98
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Host exec environment sanitization misses package, registry, Docker, compiler, and TLS override variables

## Current Maintainer Triage
- Normalized severity: medium
- Assessment: v2026.3.28 also misses the broader package, registry, compiler, Docker, and TLS env family in the shipped host-env policy, and the unreleased main fix means this is a real medium-severity open issue.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `eb8de6715f02949c21c4e895fffc8a6dcb00975c` — 2026-03-31T19:37:43+09:00

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cg7q-fg22-4g98
- https://github.com/openclaw/openclaw/commit/eb8de6715f02949c21c4e895fffc8a6dcb00975c
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-insufficient-environment-variable-sanitization-in-host-execution
