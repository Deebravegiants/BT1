# [H] OpenClaw: Workspace `.env` can override the bundled hooks root and load attacker hook code

## Summary
Severity: High
Advisory: GHSA-3qpv-xf3v-mm45
CVE: CVE-2026-41336
CWE: CWE-15, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-3qpv-xf3v-mm45
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Workspace `.env` can override the bundled hooks root and load attacker hook code

## Current Maintainer Triage
- Status: open
- Normalized severity: high
- Assessment: v2026.3.28 still lets workspace .env override OPENCLAW_BUNDLED_HOOKS_DIR, which can replace trusted default-on bundled hooks from an untrusted workspace.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `330a9f98cb29c79b1c16a2117e03d6276a0d6289` — 2026-03-31T19:25:12+09:00

OpenClaw thanks @nexrin for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3qpv-xf3v-mm45
- https://nvd.nist.gov/vuln/detail/CVE-2026-41336
- https://github.com/openclaw/openclaw/commit/330a9f98cb29c79b1c16a2117e03d6276a0d6289
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-arbitrary-hook-code-execution-via-openclaw-bundled-hooks-dir-environment-variable-override
