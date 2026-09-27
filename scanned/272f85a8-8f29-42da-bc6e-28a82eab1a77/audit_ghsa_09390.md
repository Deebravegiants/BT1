# [H] OpenClaw: MCP loopback owner context is derived from server-issued bearer tokens

## Summary
Severity: High
Advisory: GHSA-r6xh-pqhr-v4xh
CVE: CVE-2026-44118
CWE: CWE-284, CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-r6xh-pqhr-v4xh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
MCP loopback owner context is derived from server-issued bearer tokens.

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
The loopback MCP path accepted spoofable owner-context metadata from request headers, which could allow a non-owner loopback client to present itself as owner for owner-gated operations.

## Fix
The MCP loopback runtime now issues separate owner and non-owner bearer tokens and derives senderIsOwner exclusively from which token authenticated the request. The spoofable sender-owner header is no longer emitted or trusted.

## Fix Commit(s)
- 3cb1a56bfc9579a0f2336f9cfa12a8a744332a19

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

OpenClaw thanks @VladimirEliTokarev for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r6xh-pqhr-v4xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-44118
- https://github.com/openclaw/openclaw/commit/3cb1a56bfc9579a0f2336f9cfa12a8a744332a19
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-owner-context-spoofing-via-bearer-token-header
