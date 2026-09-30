# [M] OpenClaw: Sandbox file operations use check-then-act, bypassing fd-based TOCTOU defenses

## Summary
Severity: Medium
Advisory: GHSA-rm5c-4rmf-vvhw
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-rm5c-4rmf-vvhw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Sandbox file operations use check-then-act, bypassing fd-based TOCTOU defenses

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Released workspace-only apply_patch remove and mkdir operations were still check-then-act, but the draft overstates scope by bundling broader edit paths; keep it open but narrow it to the actual sandbox-workspace mutation boundary.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `32a4a47d602e0618f87b3e59f94d8c142767f860` — 2026-03-30T16:49:49+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rm5c-4rmf-vvhw
- https://github.com/openclaw/openclaw/commit/32a4a47d602e0618f87b3e59f94d8c142767f860
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
