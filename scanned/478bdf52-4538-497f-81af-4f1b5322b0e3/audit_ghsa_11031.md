# [M] OpenClaw's image tool bypasses tools.fs.workspaceOnly on sandbox mount paths and exfiltrates out-of-workspace images

## Summary
Severity: Medium
Advisory: GHSA-q6qf-4p5j-r25g
CVE: CVE-2026-32002
CWE: CWE-200, CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-q6qf-4p5j-r25g
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.23

## Details
### Summary
In OpenClaw, the sandboxed `image` tool did not honor `tools.fs.workspaceOnly=true` for mounted paths resolved by the sandbox FS bridge. This allowed reading out-of-workspace mounted images (for example `/agent/*`) and forwarding those bytes to vision model providers.

### Impact
Sandbox boundary bypass with confidentiality impact. In affected versions, `read`/`write`/`edit` respected workspace-only guardrails, but `image` could still load mounted out-of-workspace files and exfiltrate them via model requests.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.22-2`
- Patched versions: `>= 2026.2.23` (released)
- Latest published npm at triage time: `2026.2.22-2`

### Technical Details
`workspaceOnly` was enforced in sandbox file tools and `apply_patch`, but not propagated/enforced for `image` sandbox path resolution. The fix threads `workspaceOnly` into image-tool construction and asserts sandbox-root containment before loading media bytes.

### Fix Commit(s)
- `dd9d9c1c609dcb4579f9e57bd7b5c879d0146b53`

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q6qf-4p5j-r25g
- https://nvd.nist.gov/vuln/detail/CVE-2026-32002
- https://github.com/openclaw/openclaw/commit/dd9d9c1c609dcb4579f9e57bd7b5c879d0146b53
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sandbox-boundary-bypass-via-image-tool-workspaceonly-bypass
