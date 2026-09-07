# [H] OpenClaw: Workspace dotenv could override runtime-control environment variables

## Summary
Severity: High
Advisory: GHSA-hxvm-xjvf-93f3
CVE: CVE-2026-44114
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-hxvm-xjvf-93f3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.4.20`
- Patched version: `2026.4.20`

## Impact

Workspace `.env` loading did not reserve the `OPENCLAW_` runtime-control namespace broadly enough. A malicious workspace could set variables such as `OPENCLAW_GIT_DIR` before source-update or installer flows, potentially steering trusted OpenClaw runtime behavior.

This requires running OpenClaw from an attacker-controlled workspace. Severity is medium.

## Fix

OpenClaw now reserves the workspace `OPENCLAW_` environment namespace and rejects workspace dotenv entries for OpenClaw runtime-control variables.

Fix commit:

- `018494fa3ebb9145112e68b56fe1cb2e9f9a9ed6`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hxvm-xjvf-93f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44114
- https://github.com/openclaw/openclaw/commit/018494fa3ebb9145112e68b56fe1cb2e9f9a9ed6
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-environment-variable-namespace-collision-via-workspace-dotenv
