# [M] OpenClaw has a workspace-only sandbox guard mismatch for @-prefixed absolute paths

## Summary
Severity: Medium
Advisory: GHSA-27cr-4p5m-74rj
CVE: CVE-2026-32033
CWE: CWE-180, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-27cr-4p5m-74rj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
A workspace-only file-system guard mismatch allowed `@`-prefixed absolute paths to bypass boundary validation in some tool path checks.

### Impact
When `tools.fs.workspaceOnly=true`, certain `@`-prefixed absolute paths (for example `@/etc/passwd`) could be validated before canonicalization while runtime path handling normalized the prefix differently. In affected code paths this could permit reads outside the intended workspace boundary.

Per `SECURITY.md`, OpenClaw is primarily a personal-assistant runtime with trusted-user assumptions, and this path is gated behind non-default sandbox/tooling configuration. That reduces practical exposure, but the bypass is still a security bug and is fixed.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published at triage time: `2026.2.23`
- Affected versions: `<= 2026.2.23`
- Patched versions: `>= 2026.2.24`

### Fix Commit(s)
- `9ef0fc2ff8fa7b145d1e746d6eb030b1bf692260`

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-27cr-4p5m-74rj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32033
- https://github.com/openclaw/openclaw/commit/9ef0fc2ff8fa7b145d1e746d6eb030b1bf692260
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-path-traversal-via-prefixed-absolute-paths-in-workspace-boundary-validation
