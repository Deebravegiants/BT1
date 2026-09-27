# [M] OpenClaw: OpenShell FS bridge reads pin and verify the opened file before returning bytes

## Summary
Severity: Medium
Advisory: GHSA-5h3g-6xhh-rg6p
CVE: CVE-2026-44113
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-5h3g-6xhh-rg6p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
OpenShell FS bridge reads pin and verify the opened file before returning bytes 

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
A time-of-check/time-of-use race around OpenShell sandbox filesystem reads could let a symlink swap cause bytes outside the intended mount root to be read.

## Fix
OpenShell reads now open the file with no-follow semantics where available, validate the pinned file descriptor against the canonical mount root, reject unsafe hardlink/symlink cases, and use a strict fallback ancestor walk on platforms without fd-path readback.

## Fix Commit(s)
- 95119017c847c737bd113f0bff728c4666d79c45

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

Thanks @VladimirEliTokarev for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5h3g-6xhh-rg6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-44113
- https://github.com/openclaw/openclaw/commit/95119017c847c737bd113f0bff728c4666d79c45
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-time-of-check-time-of-use-race-condition-in-openshell-fs-bridge
