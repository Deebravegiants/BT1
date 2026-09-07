# [H] OpenClaw gateway exec allow-always over-trusts positional carrier executables

## Summary
Severity: High
Advisory: GHSA-p4x4-2r7f-wjxg
CVE: CVE-2026-41380
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-p4x4-2r7f-wjxg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Allow-always persistence could trust wrapper carrier executables instead of the actual invoked target when commands were routed through dispatch wrappers.

## Impact

A one-time approval could persist a broader future allowlist entry than the operator intended, weakening execution approval boundaries.

## Affected Component

`src/infra/exec-approvals-allowlist.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `9ec44fad39` (`Exec approvals: reject wrapper carrier allow-always targets`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p4x4-2r7f-wjxg
- https://github.com/openclaw/openclaw/commit/9ec44fad390f0bc1c29c3cc418b322560cb0222b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.28
