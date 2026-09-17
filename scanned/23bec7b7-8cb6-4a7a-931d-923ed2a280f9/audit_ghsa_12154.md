# [H] OpenClaw's sandbox bind validation could bypass allowed-root and blocked-path checks via symlink-parent missing-leaf paths

## Summary
Severity: High
Advisory: GHSA-m8v2-6wwh-r4gc
CVE: CVE-2026-27523
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-m8v2-6wwh-r4gc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
### Summary
In `openclaw` up to and including **2026.2.23** (latest npm release as of **February 24, 2026**), sandbox bind-source validation could be bypassed when a bind source used a symlinked parent plus a non-existent leaf path.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `<= 2026.2.23`
- Patched: `>= 2026.2.24` (planned next release)

### Root Cause
`validateBindMounts` previously relied on full-path realpath only when the full source path already existed. For missing-leaf paths, parent symlink traversal was not fully canonicalized before allowed-root and blocked-path checks.

### Security Impact
A source path that looked inside an allowed root could resolve outside that root (including blocked runtime paths) once the missing leaf was created, weakening sandbox bind-source boundary enforcement.

### Fix
The validation path now canonicalizes through the nearest existing ancestor, then always re-checks the canonical path against both:
- allowed source roots
- blocked runtime paths

### Verification
- `pnpm check`
- `pnpm exec vitest run --config vitest.gateway.config.ts`
- `pnpm test:fast`
- Added regression tests for symlink-parent + missing-leaf bypass patterns.

### Fix Commit(s)
- `b5787e4abba0dcc6baf09051099f6773c1679ec1`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.24`) so after npm publish the advisory can be published without further field edits.

OpenClaw thanks @tdjackey for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-m8v2-6wwh-r4gc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27523
- https://github.com/openclaw/openclaw/commit/b5787e4abba0dcc6baf09051099f6773c1679ec1
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sandbox-bind-validation-bypass-via-symlink-parent-missing-leaf-paths
