# [M] OpenClaw has a Path Traversal in Browser Download Functionality

## Summary
Severity: Medium
Advisory: GHSA-xwjm-j929-xq7c
CVE: CVE-2026-26972
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-xwjm-j929-xq7c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.12 <2026.2.13

## Details
### Summary

OpenClaw browser download helpers accepted an unsanitized output path. When invoked via the browser control gateway routes, this allowed path traversal to write downloads outside the intended OpenClaw temp downloads directory.

This issue is not exposed via the AI agent tool schema (no `download` action). Exploitation requires authenticated CLI access or an authenticated gateway RPC token.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: >=2026.1.12, <=2026.2.12
- Fixed: >=2026.2.13

### Details

Affected code: `src/browser/pw-tools-core.downloads.ts` (`waitForDownloadViaPlaywright`, `downloadViaPlaywright`).

Fixed entrypoints (as of 2026.2.13):
- Gateway browser control routes `/wait/download` and `/download` now restrict `path` to `DEFAULT_DOWNLOAD_DIR` via `resolvePathWithinRoot`.

### Fix Commit(s)

- 7f0489e4731c8d965d78d6eac4a60312e46a9426

### Mitigation

Upgrade to `openclaw` >=2026.2.13.

Thanks @locus-x64 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xwjm-j929-xq7c
- https://nvd.nist.gov/vuln/detail/CVE-2026-26972
- https://github.com/openclaw/openclaw/commit/7f0489e4731c8d965d78d6eac4a60312e46a9426
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.13
