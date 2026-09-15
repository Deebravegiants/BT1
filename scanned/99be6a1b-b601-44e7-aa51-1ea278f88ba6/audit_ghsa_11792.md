# [H] OpenClaw has a gateway exec allowlist allow-always bypass via unregistered /usr/bin/script wrapper

## Summary
Severity: High
Advisory: GHSA-6pfc-6m7w-m8fx
CVE: CVE-2026-41390
CWE: CWE-385
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-6pfc-6m7w-m8fx
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Allow-always persistence did not unwrap `/usr/bin/script` and similar wrappers to the actual executed target before storing trust decisions.

## Impact

A user approval for one wrapped command could persist trust for a wrapper binary that later executed a different underlying program.

## Affected Component

`src/infra/dispatch-wrapper-resolution.ts, src/infra/exec-wrapper-resolution.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `83da3cfe31` (`infra: unwrap script wrapper approval targets`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6pfc-6m7w-m8fx
- https://github.com/openclaw/openclaw/commit/83da3cfe31f016841e1deedda1a604696f4c488d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.28
