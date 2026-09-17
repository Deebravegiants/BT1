# [H] OpenClaw: Hardlink alias checks could bypass workspace-only file boundaries in specific configurations

## Summary
Severity: High
Advisory: GHSA-3jx4-q2m7-r496
CWE: CWE-59, CWE-668
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-3jx4-q2m7-r496
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.25

## Details
### Summary
In certain workspace-restricted configurations, OpenClaw could follow hardlink aliases inside the workspace that reference files outside the workspace boundary.

By default, `tools.fs.workspaceOnly` is off. This primarily affects deployments that intentionally enable workspace-only filesystem restrictions (and workspace-only `apply_patch` checks).

### Impact
- Confidentiality: out-of-workspace files could be read through in-workspace hardlink aliases.
- Integrity: out-of-workspace files could be modified through in-workspace hardlink aliases.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version at triage time: `2026.2.24`
- Affected range: `<= 2026.2.24`
- Planned patched version: `2026.2.25`

### Fix Commit(s)
- `04d91d0319b82fd4de91ed05e9fc5219ff2ab64e` (main)

### Remediation
OpenClaw now rejects hardlinked final-file aliases during workspace boundary validation for:
- workspace-only path checks (`read` / `write` / `edit`)
- workspace-only `apply_patch` read/write paths
- sandbox mount-root path-safety checks

Regression tests were added for `apply_patch`, workspace fs tools, and sandbox fs bridge hardlink alias escapes.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3jx4-q2m7-r496
- https://github.com/openclaw/openclaw/commit/04d91d0319b82fd4de91ed05e9fc5219ff2ab64e
- https://github.com/openclaw/openclaw
