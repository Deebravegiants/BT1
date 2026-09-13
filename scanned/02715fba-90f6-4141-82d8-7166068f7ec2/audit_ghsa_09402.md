# [M] OpenClaw's ACP child sessions inherit subagent security envelope constraints

## Summary
Severity: Medium
Advisory: GHSA-q3jj-46pq-826r
CVE: CVE-2026-44997
CWE: CWE-277
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-q3jj-46pq-826r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
ACP child sessions inherit subagent security envelope constraints.

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
A restricted subagent spawning an ACP child session could fail to carry forward subagent-only constraints such as depth, child-count limits, control scope, or target-agent restrictions.

## Fix
ACP spawn now resolves and persists child subagent envelope fields, enforces maximum depth and active-child caps, and applies the inherited control scope to child ACP sessions.

## Fix Commit(s)
- 31160dc069b7cc5d833b39c53736a41ad3befda2

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

OpenClaw thanks @zsxsoft, @qclawer, and @KeenSecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q3jj-46pq-826r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44997
- https://github.com/openclaw/openclaw/commit/31160dc069b7cc5d833b39c53736a41ad3befda2
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-security-envelope-constraint-bypass-in-acp-child-sessions
