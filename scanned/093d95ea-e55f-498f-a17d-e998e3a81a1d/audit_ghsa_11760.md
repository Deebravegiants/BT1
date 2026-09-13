# [M] OpenClaw has Canvas route hardening for mixed-trust deployments

## Summary
Severity: Medium
Advisory: GHSA-cjv3-m589-v3rx
CWE: CWE-1021, CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-cjv3-m589-v3rx
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
## Summary
This advisory tracks a defense-in-depth hardening for canvas routes. In mixed-trust or network-visible deployments, prior canvas auth/fallback behavior could broaden access beyond intended boundaries.

## Deployment Context
OpenClaw’s default model is trusted host + loopback-first access. Some operators intentionally expose canvas routes on LAN/tailnet. This update is aimed at those broader deployment patterns.

## What Changed
- Require explicit token or session-capability authorization for canvas routes.
- Remove shared-IP fallback paths for canvas access.
- Tighten bind/fallback behavior to fail closed.

## Impact
Risk was highest in non-loopback or mixed-trust environments. In strict single-operator trusted-host setups, practical exposure is lower.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable: `<= 2026.2.19-2`
- Patched: `2026.2.21` (next release target)

## Fix Commit(s)
- `c45f3c5b004c8d63dc0e282e2176f8c9355d24f1`
- `08a7967936cfc0b2af6b27ec1f9272542648ad6c`

Thanks @NucleiAv for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cjv3-m589-v3rx
- https://github.com/openclaw/openclaw/commit/08a7967936cfc0b2af6b27ec1f9272542648ad6c
- https://github.com/openclaw/openclaw/commit/c45f3c5b004c8d63dc0e282e2176f8c9355d24f1
- https://github.com/openclaw/openclaw
