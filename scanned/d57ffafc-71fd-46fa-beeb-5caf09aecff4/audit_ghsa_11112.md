# [H] OpenClaw: Sandboxed sessions_spawn(runtime="acp") bypassed sandbox inheritance and allowed host ACP initialization

## Summary
Severity: High
Advisory: GHSA-474h-prjg-mmw3
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-474h-prjg-mmw3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary
Sandboxed `sessions_spawn(runtime="acp")` could bypass sandbox inheritance and initialize host-side ACP runtime. The fix now fail-closes ACP spawn from sandboxed requester sessions and rejects `sandbox="require"` for `runtime="acp"`.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage time: `2026.3.1` (March 2, 2026)
- Vulnerable range: `<=2026.3.1`
- Patched release: `2026.3.2` (released)

### Technical Details
- Root cause: `runtime="subagent"` enforced sandbox inheritance, while `runtime="acp"` did not enforce equivalent sandbox/runtime checks.
- Security impact: sandbox-boundary bypass into host-side ACP initialization.
- Fixed behavior:
  - deny ACP spawn when requester runtime is sandboxed
  - deny `sessions_spawn` with `runtime="acp", sandbox="require"`
  - align sandboxed prompt guidance to avoid advertising blocked ACP paths

### Fix Commit(s)
- `ac11f0af731d41743ba02d8595f4d0fe747336e3`
- `c703aa0fe92df9fb71cf254fc46991e05fba2114`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-474h-prjg-mmw3
- https://github.com/openclaw/openclaw/commit/ac11f0af731d41743ba02d8595f4d0fe747336e3
- https://github.com/openclaw/openclaw/commit/c703aa0fe92df9fb71cf254fc46991e05fba2114
- https://github.com/openclaw/openclaw
