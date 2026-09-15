# [M] OpenClaw: SSH-based sandbox backends pass unsanitized process.env to child processes

## Summary
Severity: Medium
Advisory: GHSA-j9pv-rrcj-6pfx
CWE: CWE-212
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-j9pv-rrcj-6pfx
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
SSH-based sandbox backends pass unsanitized process.env to child processes

## Current Maintainer Triage
- Status: narrow
- Normalized severity: low
- Assessment: Shipped SSH sandbox paths leaked unsanitized env into local SSH child processes, but remote leakage needs non-default SSH env forwarding, so lower to low.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `cfe14459531e002a1c61c27d97ec7dc8aecddc1f` — 2026-03-30T20:05:57+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j9pv-rrcj-6pfx
- https://github.com/openclaw/openclaw/commit/cfe14459531e002a1c61c27d97ec7dc8aecddc1f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
