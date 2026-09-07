# [H] OpenClaw has gateway plugin auth bypass via encoded dot-segment traversal in protected /api/channels paths

## Summary
Severity: High
Advisory: GHSA-mwxv-35wr-4vvj
CVE: CVE-2026-32036
CWE: CWE-22, CWE-289
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-mwxv-35wr-4vvj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
### Summary
Gateway plugin route auth protection for `/api/channels` could be bypassed using encoded dot-segment traversal (for example `..%2f`) in path variants that plugin handlers normalize.

### Affected Packages / Versions
- Package: npm `openclaw`
- Latest published vulnerable version: `2026.2.25`
- Vulnerable version range: `<= 2026.2.25`
- Patched version: `2026.2.26` (planned next release)

### Impact
Under affected versions, crafted alternate paths could bypass gateway auth checks for protected plugin channel routes when plugin handlers decode/canonicalize the incoming path and then route to `/api/channels/...` handlers.

### Fix Commit(s)
- `258d615c45527ffda37cecd08cd268f97461bde0`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.26`). After npm publish, maintainers only need to publish the advisory.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mwxv-35wr-4vvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32036
- https://github.com/openclaw/openclaw/commit/258d615c45527ffda37cecd08cd268f97461bde0
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-encoded-dot-segment-traversal-in-api-channels
