# [H] OpenClaw has Inconsistent Host Exec Environment Override Sanitization

## Summary
Severity: High
Advisory: GHSA-39pp-xp36-q6mg
CVE: CVE-2026-35650
CWE: CWE-15, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-39pp-xp36-q6mg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Gateway host exec env override handling did not consistently apply the shared host environment policy, so blocked or malformed override keys could slip through inconsistent sanitization paths.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `7abfff756d6c68d17e21d1657bbacbaec86de232`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/infra/host-env-security.ts now provides one shared sanitizer and fail-closed diagnostics for blocked or malformed override keys.
- src/agents/bash-tools.exec.ts and src/node-host/invoke-system-run.ts both route env overrides through the shared sanitizer before execution.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-39pp-xp36-q6mg
- https://nvd.nist.gov/vuln/detail/CVE-2026-35650
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/7abfff756d6c68d17e21d1657bbacbaec86de232
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-environment-variable-override-bypass-via-inconsistent-sanitization
