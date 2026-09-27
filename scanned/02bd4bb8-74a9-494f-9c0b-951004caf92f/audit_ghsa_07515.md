# [M] mcp-memory-keeper: Arbitrary local file read in context_import via unvalidated filePath

## Summary
Severity: Medium
Advisory: GHSA-f7wf-v2vw-mpcx
CVE: CVE-2026-54561
CWE: CWE-209, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-17
Source: https://github.com/advisories/GHSA-f7wf-v2vw-mpcx
Type: github-advisory

## Affected
- npm: `mcp-memory-keeper` — affected >=0 <0.13.0

## Details
### Impact

`context_import` passed the caller-supplied `filePath` directly to `fs.readFileSync` with no path confinement. A malicious MCP client — or an LLM agent that is prompt-injected into calling the tool — could point `filePath` at **any file readable by the server process**, outside any session or export directory:

- **Full disclosure (JSON files):** a valid-JSON target (e.g. another user's exported session, or a `*.json` credential / service-account file) is parsed and imported into the caller's session, then retrievable verbatim via `context_get` / `context_export`.
- **Partial disclosure (any file):** for a non-JSON target (e.g. `/etc/passwd`, an SSH key, a `.env`), `JSON.parse` throws and V8 includes a snippet of the file's leading bytes in the `SyntaxError` message, which was returned verbatim to the caller.

Both `../` traversal and absolute paths worked — there was no path confinement of any kind.

In a typical MCP deployment the server runs on the developer's machine, so the reachable set includes other users' exported memory sessions, JSON credential/config files, and (in leading-bytes form) `.env` files, SSH keys, and `/etc/passwd`. The trigger is a tool argument, so the realistic threat model is an LLM agent prompt-injected into calling `context_import`, or any MCP client connected to the server.

### Patches

Fixed in **0.13.0** (PR #36):

- Imports are confined to a server-owned exports directory (`<DATA_DIR>/exports`, overridable via `MEMORY_KEEPER_EXPORT_DIR`), resolved with `realpathSync`. `../` traversal, absolute paths outside the directory, and symlink escapes are all rejected.
- File read and `JSON.parse` are separate operations; read/parse failures return a generic message and never echo file bytes (the `SyntaxError`-message leak is gone). The database-write path is likewise generic.
- An E2E security regression suite covers the reported arbitrary-read and traversal vectors, plus symlink escape, the directory-prefix boundary, and a no-existence-oracle check.

### Workarounds

Upgrade to **`>= 0.13.0`**. There is no configuration-only workaround for affected versions.

### Resources

- Report: GitHub issue #35
- Fix: PR #36

### Credit

Reported by Zhihao Zhang ([@mcfly-zzh](https://github.com/mcfly-zzh)).

## References
- https://github.com/mkreyman/mcp-memory-keeper/security/advisories/GHSA-f7wf-v2vw-mpcx
- https://github.com/mkreyman/mcp-memory-keeper/issues/35
- https://github.com/mkreyman/mcp-memory-keeper/pull/36
- https://github.com/mkreyman/mcp-memory-keeper/commit/84f6dfa692736a34ff36e2d2cf2188b71facf73b
- https://github.com/mkreyman/mcp-memory-keeper
- https://github.com/mkreyman/mcp-memory-keeper/releases/tag/v0.13.0
