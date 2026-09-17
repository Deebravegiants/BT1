# [M] OpenClaw: Hook mapping templates could bypass hook session-key opt-in

## Summary
Severity: Medium
Advisory: GHSA-2xcp-x87w-q377
CVE: CVE-2026-45002
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-2xcp-x87w-q377
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.4.20`
- Patched version: `2026.4.20`

## Impact

Templated hook mapping `sessionKey` values were treated differently from request-supplied session keys. A hook mapping could render an externally influenced session key even when `hooks.allowRequestSessionKey` was disabled, bypassing the intended routing opt-in for hook callers.

This affects webhook routing isolation. It does not grant host execution by itself. Severity is medium.

## Fix

Template-rendered mapping session keys are now treated as externally supplied routing input and require `hooks.allowRequestSessionKey=true` plus the existing prefix policy checks.

Fix commit:

- `5275d008ed33203dba3f98e969ad683a65c416c3`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2xcp-x87w-q377
- https://nvd.nist.gov/vuln/detail/CVE-2026-45002
- https://github.com/openclaw/openclaw/commit/5275d008ed33203dba3f98e969ad683a65c416c3
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-hook-session-key-bypass-via-template-mapping
