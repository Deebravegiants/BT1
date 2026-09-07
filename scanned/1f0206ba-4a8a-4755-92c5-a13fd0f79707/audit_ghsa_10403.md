# [H] OpenClaw: Paired node escalates to gateway RCE via unrestricted node.event agent dispatch

## Summary
Severity: High
Advisory: GHSA-gjm7-hw8f-73rq
CVE: CVE-2026-41378
CWE: CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-gjm7-hw8f-73rq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Paired node escalates to gateway RCE via unrestricted node.event agent dispatch

## Current Maintainer Triage
- Status: narrow
- Normalized severity: high
- Assessment: v2026.3.28 still lets paired role=node clients drive node.event agent.request into broader gateway-side tool access than node RPCs, but critical is overstated because a trusted paired node foothold is already required.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `a77928b1087e90f2a8903f8e5aca6dec9237ac62` — 2026-03-30T14:22:15+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gjm7-hw8f-73rq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41378
- https://github.com/openclaw/openclaw/commit/a77928b1087e90f2a8903f8e5aca6dec9237ac62
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-to-remote-code-execution-via-unrestricted-node-event-agent-dispatch
