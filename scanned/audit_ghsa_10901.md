# [M] OpenClaw's Zalo group sender allowlist bypass permits unauthorized GROUP dispatch

## Summary
Severity: Medium
Advisory: GHSA-534w-2vm4-89xr
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-534w-2vm4-89xr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
A missing group-sender authorization check in the Zalo plugin allowed unauthorized `GROUP` messages to enter agent dispatch paths in configurations intended to restrict group traffic.

## Impact
When Zalo group handling was configured with allowlist-style controls, a sender not present in the intended group allowlist could still trigger agent processing through the `GROUP` message path.

## Root Cause
Group access checks were not consistently enforced before dispatch for Zalo `GROUP` messages. The fix adds explicit runtime group-policy evaluation (`groupPolicy`, `groupAllowFrom`, fallback to `allowFrom`) and fail-closed behavior for missing provider config.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published vulnerable version: `2026.2.23` (as of 2026-02-24)
- Affected range: `<= 2026.2.23`
- Planned patched version: `2026.2.24`

## Fix Commit(s)
- `b4010a0b627025c809c0e5dbdbd4770f3bc59ef8`

OpenClaw thanks @tdjackey for reporting.

### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-534w-2vm4-89xr
- https://github.com/openclaw/openclaw/commit/b4010a0b627025c809c0e5dbdbd4770f3bc59ef8
- https://github.com/openclaw/openclaw
