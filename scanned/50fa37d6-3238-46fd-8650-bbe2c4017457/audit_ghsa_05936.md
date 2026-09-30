# [H] faf-mcp has an arbitrary local file read/write via unconfined `path` argument in FAF tools

## Summary
Severity: High
Advisory: GHSA-j4r7-8ph4-43g3
CWE: CWE-200, CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-j4r7-8ph4-43g3
Type: github-advisory

## Affected
- npm: `faf-mcp` — affected >=0 <2.1.3

## Details
### Summary
`faf-mcp` MCP tools accept a caller-controlled `path` argument and resolve it (`~` expansion + `path.resolve()`) straight into a filesystem read/write **without confining it to a trusted project directory**. An absolute path or `../` traversal is resolved and used as-is, so the server process can be made to read — and, via the file tools, write — files outside the intended `.faf` project context. The only remaining limit is OS file permissions.

### Affected tools
The shared `getProjectPath()` chokepoint (feeding the `.faf` tools) and the general-purpose `faf_read` / `faf_write` file tools resolved a caller path straight into a read/write with no confinement (denylist-only); an absolute path still reached home-directory secrets, and `faf_write` could write outside the project.

### Impact
An MCP client — or an LLM prompt-injected via attacker-controlled content (a web page, README, ticket, or `.faf`) into issuing a tool call — can read any file the server process can read: SSH keys (`~/.ssh/id_rsa`), cloud credentials (`~/.aws/credentials`), `.env` files, source, `/etc/passwd`; and `faf_write` could write outside the project. This is a sensitive-information-disclosure (CWE-200) primitive that far exceeds the declared `.faf` project-context scope. The server runs over stdio, so the read/write is reached by a crafted tool call (e.g. a prompt-injected agent processing attacker-controlled content).

### Patches
Fixed in **2.1.3** by confining every caller-supplied `path` before any filesystem access (`safe-path.ts`):
- Reads are restricted to `.faf` / `.fafm` context files, so non-context files (secrets) are refused regardless of directory.
- General file ops (`faf_read` / `faf_write`) are confined to the project root (cwd + system temp; override with `FAF_ALLOWED_ROOTS`).
- Paths are canonicalized through symlinks (closing the symlink bypass); absolute paths and `../` escapes are rejected; `callTool()` gains a central PATH-DENIED guard.

Upgrade: `npm install -g faf-mcp@2.1.3` (or `npx faf-mcp`).

### Workarounds
If you cannot upgrade immediately, run the server only against trusted local projects, and set `FAF_ALLOWED_ROOTS` (patched versions) to a single project directory for a hard directory boundary.

### Credits
Identified by the maintainers during a sibling-server audit prompted by the coordinated disclosure of the same class of issue in `grok-faf-mcp` by **Zhihao Zhang** (Worcester Polytechnic Institute).

## References
- https://github.com/Wolfe-Jam/faf-mcp/security/advisories/GHSA-j4r7-8ph4-43g3
- https://github.com/Wolfe-Jam/faf-mcp
- https://github.com/Wolfe-Jam/faf-mcp/releases/tag/v2.1.3
