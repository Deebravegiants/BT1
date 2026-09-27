# [M] OpenClaw has pre-auth webhook body parsing that can enable unauthenticated slow-request DoS

## Summary
Severity: Medium
Advisory: GHSA-x4vp-4235-65hg
CVE: CVE-2026-32011
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-x4vp-4235-65hg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
## Impact

OpenClaw webhook handlers for BlueBubbles and Google Chat accepted and parsed request bodies before authentication and signature checks on vulnerable releases. This allowed unauthenticated clients to hold parser work open with slow/oversized request bodies and degrade availability (slow-request DoS).

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected releases: `<= 2026.3.1`
- Latest published vulnerable version at triage time: `2026.3.1` (npm)
- Fixed release: `2026.3.2` (released)

## Fix Commit(s)

- `d3e8b17aa6432536806b4853edc7939d891d0f25`

## Mitigation

Upgrade to `2026.3.2` (or newer). The fix enforces auth-before-body for affected webhook paths, adds strict pre-auth body/time budgets, and introduces shared in-flight/request guardrails with regression coverage.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x4vp-4235-65hg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32011
- https://github.com/openclaw/openclaw/commit/d3e8b17aa6432536806b4853edc7939d891d0f25
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-slow-request-denial-of-service-via-pre-auth-webhook-body-parsing
