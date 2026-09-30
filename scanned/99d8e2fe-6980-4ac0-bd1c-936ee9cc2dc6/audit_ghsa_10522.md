# [M] OpenClaw: Workspace dotenv MiniMax host override could redirect credentialed requests

## Summary
Severity: Medium
Advisory: GHSA-h2vw-ph2c-jvwf
CVE: CVE-2026-44992
CWE: CWE-15, CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:P/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-h2vw-ph2c-jvwf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.4.5 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `>= 2026.4.5, < 2026.4.20`
- Patched version: `2026.4.20`

## Impact

A malicious workspace `.env` could set `MINIMAX_API_HOST` and redirect credentialed MiniMax requests to an attacker-controlled origin, exposing the MiniMax API key in the outbound `Authorization` header.

This requires running OpenClaw from an attacker-controlled workspace. Severity is medium.

## Fix

OpenClaw now blocks `MINIMAX_API_HOST` from workspace dotenv injection and removes env-driven URL routing from the affected MiniMax request path.

Fix commit:

- `2f06696579a1ab0cb5bbbbb6a900414a6b2e3cd1`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h2vw-ph2c-jvwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44992
- https://github.com/openclaw/openclaw/commit/2f06696579a1ab0cb5bbbbb6a900414a6b2e3cd1
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-minimax-api-host-override-via-workspace-dotenv
