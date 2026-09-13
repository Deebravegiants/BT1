# [M] OpenClaw: Image Tool `tools.fs.workspaceOnly` Bypass via Sandbox Bridge Mounts

## Summary
Severity: Medium
Advisory: GHSA-cfp9-w5v9-3q4h
CVE: CVE-2026-35658
CWE: CWE-668, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-cfp9-w5v9-3q4h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
## Summary
The `image` tool did not fully honor the `tools.fs.workspaceOnly` filesystem boundary. In affected releases, image-path resolution could still traverse sandbox bridge mounts outside the workspace and read files from mounted directories that the other file tools would reject.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `< 2026.3.2`
- Fixed: `>= 2026.3.2`
- Latest released tags checked: `v2026.3.23` (`ccfeecb6887cd97937e33a71877ad512741e82b2`) and `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `dd9d9c1c609dcb4579f9e57bd7b5c879d0146b53`
- `14baadda2c456f3cf749f1f97e8678746a34a7f4`

## Release Status
The complete fix shipped in `v2026.3.2` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- `src/agents/openclaw-tools.ts` now passes `fsPolicy` into `createImageTool`, so the image tool receives the same workspace-only policy input as the other filesystem tools.
- `src/agents/tools/image-tool.ts`, `src/agents/tools/media-tool-shared.ts`, and `src/agents/sandbox-media-paths.ts` now restrict local roots and sandbox-bridge resolution to the workspace when `tools.fs.workspaceOnly` is enabled.

OpenClaw thanks @YLChen-007 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cfp9-w5v9-3q4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-35658
- https://github.com/openclaw/openclaw/commit/14baadda2c456f3cf749f1f97e8678746a34a7f4
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/ccfeecb6887cd97937e33a71877ad512741e82b2
- https://github.com/openclaw/openclaw/commit/dd9d9c1c609dcb4579f9e57bd7b5c879d0146b53
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-filesystem-boundary-bypass-in-image-tool
