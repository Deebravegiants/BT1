# [M] OpenClaw has a Feishu allowFrom authorization bypass via display-name collision

## Summary
Severity: Medium
Advisory: GHSA-j4xf-96qf-rx69
CVE: CVE-2026-32021
CWE: CWE-639, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-j4xf-96qf-rx69
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary

Feishu allowlist authorization could be bypassed by display-name collision.

### Details

`channels.feishu.allowFrom` is documented as an ID-based allowlist (open_id list), but Feishu policy matching accepted mutable sender display names in the same namespace. An attacker could set a display name equal to an allowlisted ID string and pass authorization checks.

The fix enforces ID-only matching for Feishu allowlist checks, normalizes Feishu ID prefixes during comparison, and ignores mutable display names for authorization.

### Impact

Deployments using Feishu allowlist-based authorization could incorrectly authorize non-allowlisted senders when a colliding display name was used.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published version at triage time: `2026.2.21-2`
- Affected range: `<= 2026.2.21-2`
- Planned patched version: `>= 2026.2.22`

### Fix Commit(s)

- `4ed87a667263ed2d422b9d5d5a5d326e099f92c7`

### Release Process Note

`patched_versions` is pre-set to the planned next release (`>= 2026.2.22`) so the advisory is ready to publish once that npm release is available.

OpenClaw thanks @jiseoung for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j4xf-96qf-rx69
- https://nvd.nist.gov/vuln/detail/CVE-2026-32021
- https://github.com/openclaw/openclaw/commit/4ed87a667263ed2d422b9d5d5a5d326e099f92c7
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-display-name-collision-in-feishu-allowfrom
