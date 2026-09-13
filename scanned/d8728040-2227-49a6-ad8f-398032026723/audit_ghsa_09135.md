# [M] OpenClaw: OpenShell FS bridge writes stay pinned to the sandbox mount root

## Summary
Severity: Medium
Advisory: GHSA-wppj-c6mr-83jj
CVE: CVE-2026-44112
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-wppj-c6mr-83jj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
OpenShell FS bridge writes stay pinned to the sandbox mount root 

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
A time-of-check/time-of-use race around OpenShell sandbox filesystem writes could let a symlink swap redirect a write outside the intended local mount root.

## Fix
OpenShell write paths now validate the canonical target against the mount root, reject unsafe symlink parents and symlink leaves for writes, and use root-scoped write helpers before syncing to the remote sandbox.

## Fix Commit(s)
- 7be82d4fd1193bcb7e44ee38838f00bf924ffa76

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

Thanks @VladimirEliTokarev for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wppj-c6mr-83jj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44112
- https://github.com/openclaw/openclaw/commit/7be82d4fd1193bcb7e44ee38838f00bf924ffa76
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-symlink-swap-race-condition-in-openshell-fs-bridge-writes
