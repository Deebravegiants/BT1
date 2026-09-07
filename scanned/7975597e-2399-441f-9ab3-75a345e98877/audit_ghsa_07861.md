# [H] OpenClaw has a path traversal in browser trace/download output paths may allow arbitrary file writes

## Summary
Severity: High
Advisory: GHSA-gq9c-wg68-gwj2
CVE: CVE-2026-28462
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-gq9c-wg68-gwj2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.13

## Details
## Summary

  OpenClaw’s browser control API accepted user-supplied output paths for trace/download files without consistently
  constraining writes to OpenClaw-managed temporary directories.

  ## Impact

  If an attacker can access the browser control API, they could attempt to write trace/download output files outside
  intended temp roots, depending on process filesystem permissions.

  ## Affected versions

  `openclaw` `< 2026.2.13`

  ## Fixed versions

  `openclaw` `>= 2026.2.13`

  ## Remediation

  Upgrade to `2026.2.13` or later.

  ## What changed

  The fix constrains output paths for:

  - `POST /trace/stop`
  - `POST /wait/download`
  - `POST /download`

  All three now enforce OpenClaw temp-root boundaries and reject traversal/escape paths.

  ## Credits

  Thanks to Adnan Jakati (@jackhax) of Praetorian for responsible disclosure.

  Fix shipped in PR #15652 and merged to `main` on February 13, 2026 (`7f0489e4731c8d965d78d6eac4a60312e46a9426`).

---

Fix commit 7f0489e4731c8d965d78d6eac4a60312e46a9426 confirmed on main and in v2026.2.14. Upgrade to `openclaw >= 2026.2.13`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gq9c-wg68-gwj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-28462
- https://github.com/openclaw/openclaw/pull/15652
- https://github.com/openclaw/openclaw/commit/7f0489e4731c8d965d78d6eac4a60312e46a9426
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-traversal-in-trace-and-download-output-paths
