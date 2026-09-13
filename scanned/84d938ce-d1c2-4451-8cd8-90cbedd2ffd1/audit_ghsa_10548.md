# [H] OpenClaw: Device-Paired Node Skips Node Scope Gate → Host RCE.md

## Summary
Severity: High
Advisory: GHSA-xj9w-5r6q-x6v4
CVE: CVE-2026-41352
CWE: CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-xj9w-5r6q-x6v4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Device-Paired Node Skips Node Scope Gate → Host RCE.md

## Current Maintainer Triage
- Status: open
- Normalized severity: high
- Assessment: Real in shipped v2026.3.28 because a merely device-paired node could expose node commands without node pairing, but high is sufficient given the pairing/setup prerequisites.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `3886b65ef21d02808c1a106fa1f9f69e22f71c32` — 2026-03-30T17:29:28+01:00

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xj9w-5r6q-x6v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41352
- https://github.com/openclaw/openclaw/commit/3886b65ef21d02808c1a106fa1f9f69e22f71c32
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-remote-code-execution-via-node-scope-gate-bypass
