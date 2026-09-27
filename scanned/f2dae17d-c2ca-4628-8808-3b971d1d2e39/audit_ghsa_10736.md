# [H] OpenClaw: Agentic Consent Bypass — LLM Agent Can Silently Disable Exec Approval via `config.patch`

## Summary
Severity: High
Advisory: GHSA-v3qc-wrwx-j3pw
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-v3qc-wrwx-j3pw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary
Agentic Consent Bypass: LLM Agent Can Silently Disable Exec Approval via `config.patch`

## Current Maintainer Triage
- Status: open
- Normalized severity: high
- Assessment: Maintainers accepted this issue, fixed it in 76411b2afc4ae721e36c12e0ea24fd23e2fed61e on 2026-03-27, and that fix shipped in v2026.3.28, so normalize it as a fixed released draft rather than a close-by-trust-model call.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.24`
- Patched versions: `>= 2026.3.28`
- First stable tag containing the fix: `v2026.3.28`

## Fix Commit(s)
- `76411b2afc4ae721e36c12e0ea24fd23e2fed61e` — 2026-03-27T09:42:15Z

OpenClaw thanks @YLChen-007 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v3qc-wrwx-j3pw
- https://github.com/openclaw/openclaw/commit/76411b2afc4ae721e36c12e0ea24fd23e2fed61e
- https://github.com/openclaw/openclaw
