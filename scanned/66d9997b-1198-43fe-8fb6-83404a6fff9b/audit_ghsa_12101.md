# [H] OpenClaw: Experimental apply_patch may bypass workspace-only checks in opt-in sandbox mounts (off by default)

## Summary
Severity: High
Advisory: GHSA-h9xm-j4qg-fvpg
CVE: CVE-2026-32007
CWE: CWE-22, CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-h9xm-j4qg-fvpg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
### Summary
In some opt-in sandbox configurations, the **experimental** `apply_patch` tool did not consistently apply workspace-only checks to mounted paths (for example `/agent/...`).

### Impact
This does **not** affect default installs.

Default posture:
- `agents.defaults.sandbox.mode=off` (sandbox disabled by default)
- `tools.exec.applyPatch.enabled=false` (experimental tool disabled by default)

This behavior applies only when all of the following are enabled/configured:
- sandbox mode,
- experimental `apply_patch`,
- workspace-only expectations (`tools.fs.workspaceOnly=true` and/or `tools.exec.applyPatch.workspaceOnly=true`),
- and writable mounts outside workspace.

Under that opt-in setup, `apply_patch` operations could target mounted paths outside the workspace root.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected published versions: `<= 2026.2.22-2`
- Fixed in code on `main`: commit `6634030be31e1a1842967df046c2f2e47490e6bf`
- Patched release: `2026.2.23`

### Technical Details
In the sandbox path flow, `apply_patch` used `sandbox.bridge.resolvePath(...)` without applying the same workspace-root assertion used by other filesystem tools. The fix makes `apply_patch` follow the same workspace-only enforcement for sandbox-resolved paths (unless explicitly disabled with `tools.exec.applyPatch.workspaceOnly=false`).

### Fix Commit(s)
- `6634030be31e1a1842967df046c2f2e47490e6bf`

### Release Process Note
`patched_versions` is pre-set to the released version (`2026.2.23`). Patched in `2026.2.23` and published.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h9xm-j4qg-fvpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-32007
- https://github.com/openclaw/openclaw/commit/6634030be31e1a1842967df046c2f2e47490e6bf
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sandbox-bypass-in-apply-patch-tool-via-workspace-only-check-bypass
