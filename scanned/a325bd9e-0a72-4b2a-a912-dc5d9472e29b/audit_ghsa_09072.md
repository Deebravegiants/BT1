# [M] OpenClaw's Gateway Control UI bootstrap config required Gateway auth

## Summary
Severity: Medium
Advisory: GHSA-93rg-2xm5-2p9v
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-93rg-2xm5-2p9v
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
Gateway Control UI bootstrap config required Gateway auth.

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
When Gateway authentication was enabled, the Control UI bootstrap config endpoint could still be read without a valid Gateway token. That response could expose sensitive bootstrap/config fields intended only for authenticated Control UI sessions.

## Fix
The bootstrap config route now goes through the same Gateway read-auth path as other authenticated Control UI reads. Regression tests cover unauthenticated rejection, valid-token access, and basePath handling.

## Fix Commit(s)
- 2321d67263bc710e357644d59f746b08d891051b

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

OpenClaw thanks @zsxsoft for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-93rg-2xm5-2p9v
- https://github.com/openclaw/openclaw/commit/2321d67263bc710e357644d59f746b08d891051b
- https://github.com/openclaw/openclaw
