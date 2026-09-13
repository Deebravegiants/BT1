# [M] OpenClaw: Unified root-bound write hardening for browser output and related path-boundary flows

## Summary
Severity: Medium
Advisory: GHSA-3pxq-f3cp-jmxp
CVE: CVE-2026-22180
CWE: CWE-367, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-3pxq-f3cp-jmxp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary
A path-confinement bypass in browser output handling allowed writes outside intended roots in `openclaw` versions up to and including `2026.3.1`.

The fix unifies root-bound, file-descriptor-verified write semantics and canonical path-boundary validation across browser output and related install/skills write paths.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage time: `2026.3.1`
- Affected range: `<= 2026.3.1`
- Patched release: `2026.3.2` (released)

### Fix Commit(s)
- `104d32bb64cdf19d5e77f70553a511a2ae90ad1c`

### Technical Notes
- Browser output writes now use root-bound, fd/inode-verified commit flow.
- Install + skills path checks now share canonical in-base validation to reduce drift and close equivalent escape surfaces.
- Added regression coverage for symlink-rebind and root-bound source-path write behavior.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3pxq-f3cp-jmxp
- https://github.com/openclaw/openclaw/commit/104d32bb64cdf19d5e77f70553a511a2ae90ad1c
- https://github.com/openclaw/openclaw
