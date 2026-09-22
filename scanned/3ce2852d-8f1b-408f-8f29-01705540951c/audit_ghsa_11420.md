# [H] OpenClaw: workspace path guard bypass on non-existent out-of-root symlink leaf

## Summary
Severity: High
Advisory: GHSA-mgrq-9f93-wpp5
CVE: CVE-2026-32055
CWE: CWE-22, CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-mgrq-9f93-wpp5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
### Summary
`openclaw` had a workspace boundary bypass in workspace-only path validation: when an in-workspace symlink pointed outside the workspace to a non-existent leaf, the first write could pass validation and create the file outside the workspace.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.25`
- Patched versions: `>= 2026.2.26` (pre-set for next planned release)
- Latest published npm version at update time: `2026.2.25`

### Details
The boundary check path resolved aliases in a way that allowed a non-existent out-of-root symlink target to pass the initial validation window. A first write through the guarded workspace path could therefore escape the workspace boundary.

The fix hardens canonical boundary resolution so missing-leaf alias paths are evaluated against canonical containment, while preserving valid in-root aliases. This closes the first-write escape condition without regressing valid in-root alias usage.

### Fix Commit(s)
- `46eba86b45e9db05b7b792e914c4fe0de1b40a23`
- `1aef45bc060b28a0af45a67dc66acd36aef763c9`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.26`). Once npm release `2026.2.26` is published, this advisory can be published directly.

Thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mgrq-9f93-wpp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-32055
- https://github.com/openclaw/openclaw/commit/1aef45bc060b28a0af45a67dc66acd36aef763c9
- https://github.com/openclaw/openclaw/commit/46eba86b45e9db05b7b792e914c4fe0de1b40a23
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-workspace-path-boundary-bypass-via-non-existent-symlink
