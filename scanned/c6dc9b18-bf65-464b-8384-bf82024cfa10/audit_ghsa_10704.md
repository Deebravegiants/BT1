# [M] OpenClaw: pnpm dlx approvals did not bind local script operands

## Summary
Severity: Medium
Advisory: GHSA-w6wx-jq6j-6mcj
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-w6wx-jq6j-6mcj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, `pnpm dlx` approval planning did not bind local script operands the same way as related `pnpm exec` flows. A local script approved through a `pnpm dlx` path could be replaced before execution without invalidating the approval.

## Impact

An operator could approve a benign local script and then execute modified script contents through the still-valid approval plan. This was an approval-integrity bug in the node-host command-planning path.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `176c059b05357df1bc09d4328a2380670859eeff` — bind local scripts in `pnpm dlx` approval plans

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @Kazamayc for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w6wx-jq6j-6mcj
- https://github.com/openclaw/openclaw/commit/176c059b05357df1bc09d4328a2380670859eeff
- https://github.com/openclaw/openclaw
