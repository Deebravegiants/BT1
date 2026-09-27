# [M] OpenClaw has SSRF guard bypass via IPv6 transition over ISATAP

## Summary
Severity: Medium
Advisory: GHSA-8cp7-rp8r-mg77
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-8cp7-rp8r-mg77
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.20 <2026.2.19

## Details
## Summary
OpenClaw's SSRF hostname/IP guard did not detect ISATAP embedded IPv4 addresses (`...:5efe:w.x.y.z`). A crafted URL containing an ISATAP IPv6 literal could embed a private IPv4 target (for example loopback) and bypass private-address filtering in URL-fetching paths.

## Severity Assessment
Rated **medium**: the bug weakens SSRF protections in URL fetch flows, but impact depends on reaching a URL-fetching path with attacker-controlled input and is generally constrained to internal network access attempts.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `>=2026.1.20 <=2026.2.17`
- Latest published at patch time: `2026.2.17`
- Patched release: `2026.2.19`

## Security Policy Context
Per `SECURITY.md`, OpenClaw's web/gateway surface is intended for local use by default, public internet exposure is out-of-scope, and prompt-injection reports are out-of-scope for bounty handling. This advisory tracks a core SSRF-guard bypass in fetch protections.

## Impact
This can permit SSRF-style access attempts to internal/private network targets through URL ingestion/fetch paths that rely on shared hostname/IP blocking.

## Fix
- Added RFC 5214 ISATAP embedded-IPv4 detection to the shared SSRF classifier.
- Centralized hostname/IP blocking through `isBlockedHostnameOrIp` and routed relevant validators to that shared path.
- Added regression tests for ISATAP private vs public embedded IPv4 handling.

## Fix Commit(s)
- `d51929ecb52fe65e90bf36795f4247feb29eb8aa`

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8cp7-rp8r-mg77
- https://github.com/openclaw/openclaw/commit/d51929ecb52fe65e90bf36795f4247feb29eb8aa
- https://github.com/openclaw/openclaw
