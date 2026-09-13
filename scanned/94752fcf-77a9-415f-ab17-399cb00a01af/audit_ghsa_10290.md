# [H] OpenClaw: Self-Whitelisting in appendLocalMediaParentRoots Allows Arbitrary File Read & Credential Exfiltration

## Summary
Severity: High
Advisory: GHSA-57gh-m6rq-54cf
CWE: CWE-552
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-57gh-m6rq-54cf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Media Local Roots Self-Whitelisting in `appendLocalMediaParentRoots` Allows Model-Initiated Arbitrary Host File Read and Credential Exfiltration

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: v2026.3.28 still self-whitelists media parent dirs in src/media/local-roots.ts, but only after config already permits tool-fs root expansion, so the impact is narrower than the default-critical framing.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `1ca4261d7e055d0be141ed79ebb1365d0fbc7364` — 2026-03-30T17:15:03+01:00

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-57gh-m6rq-54cf
- https://github.com/openclaw/openclaw/commit/1ca4261d7e055d0be141ed79ebb1365d0fbc7364
- https://github.com/openclaw/openclaw
