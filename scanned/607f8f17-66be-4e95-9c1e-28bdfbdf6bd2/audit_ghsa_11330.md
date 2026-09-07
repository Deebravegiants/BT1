# [H] OpenClaw: Native prompt image auto-load did not honor tools.fs.workspaceOnly in sandboxed runs

## Summary
Severity: High
Advisory: GHSA-9f72-qcpw-2hxc
CWE: CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-9f72-qcpw-2hxc
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
### Summary
In sandboxed runs, native prompt image auto-load did not honor `tools.fs.workspaceOnly=true`.

This optional hardening setting is **not enabled by default**. When operators enabled it, prompt text could still reference mounted out-of-workspace image paths (for example `/agent/secret.png`) and load those image bytes for vision-capable model input.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage time: `2026.2.23`
- Vulnerable version range: `<= 2026.2.23`
- Patched version (planned next release): `2026.2.24`

### Conditions Required
This issue required all of the following:
- sandbox mode enabled,
- `tools.fs.workspaceOnly=true` configured,
- an out-of-workspace mount path reachable from the sandbox (for example `/agent`),
- vision-capable model path active for native prompt image loading.

### Technical Details
Native prompt image ingestion (`detectAndLoadPromptImages` / `loadImageFromRef`) resolved and read sandbox paths but did not apply the same workspace-root assertion used by file tools when `tools.fs.workspaceOnly` was set.

### Fix Commit(s)
- `370d115549c0dadace0902775eea0d5094aedfdc`

### Verification
- `pnpm check`
- `pnpm exec vitest run --config vitest.gateway.config.ts`
- `pnpm test:fast`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.24`) so once npm release is available, this advisory only needs publish action.

OpenClaw thanks @tdjackey for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9f72-qcpw-2hxc
- https://github.com/openclaw/openclaw/commit/370d115549c0dadace0902775eea0d5094aedfdc
- https://github.com/openclaw/openclaw
