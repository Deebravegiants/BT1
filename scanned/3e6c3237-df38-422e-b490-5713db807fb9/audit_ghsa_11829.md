# [M] OpenClaw's owner-only gateway tool access checks were incomplete in specific authenticated DM flows

## Summary
Severity: Medium
Advisory: GHSA-2hm8-rqrm-xfjq
CWE: CWE-269, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-2hm8-rqrm-xfjq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Summary

In authenticated non-owner DM sessions, a narrow tool-invocation path could reach broader-than-intended owner-only gateway actions.

## Impact

This requires an authenticated non-owner sender in a DM session and a specific tool invocation path. No unauthenticated access is involved, and this does not provide direct code execution by itself.

## Root Cause

- Some gateway call paths were still using broader default scopes instead of method-level least-privilege scopes.
- Owner-only enforcement depended on tool-name checks and was not consistently metadata-driven across all call paths.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.17` (latest published npm version as of February 19, 2026)
- Patched: `2026.2.19`

## Remediation

- Refactored gateway method scope mapping to a data-driven table and added guard tests to ensure all exposed core gateway methods stay classified.
- Centralized owner-only enforcement in tool policy wrappers and tool metadata.
- Marked owner-only tools explicitly (`cron`, `gateway`, `whatsapp_login`) and removed duplicated per-tool owner checks.
- Refactored gateway call path internals into smaller helpers while preserving behavior and coverage.

## Fix Commit(s)

- `a40c10d3e24568b1e2947c104484be74bf66b8d2`
- `2777d8ad91ef1e8a7c6f5b4b18f8507be7d02914`
- `3d7ad1cfca4daaa84cd553e843e0e08fa6201349`

OpenClaw thanks @Adam55A-code for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2hm8-rqrm-xfjq
- https://github.com/openclaw/openclaw/commit/2777d8ad91ef1e8a7c6f5b4b18f8507be7d02914
- https://github.com/openclaw/openclaw/commit/3d7ad1cfca4daaa84cd553e843e0e08fa6201349
- https://github.com/openclaw/openclaw/commit/a40c10d3e24568b1e2947c104484be74bf66b8d2
- https://github.com/openclaw/openclaw
