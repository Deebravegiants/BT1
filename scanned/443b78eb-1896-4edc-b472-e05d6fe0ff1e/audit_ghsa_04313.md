# [M] Network-AI: AgentRuntime sandbox path-prefix checks allow file access outside the configured base directory

## Summary
Severity: Medium
Advisory: GHSA-jvcm-f35g-w78p
CWE: CWE-22, CWE-23
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-jvcm-f35g-w78p
Type: github-advisory

## Affected
- npm: `network-ai` — affected >=0 <5.12.2

## Details
### Summary
`AgentRuntime` promises scoped file access under a configured sandbox `basePath`, but its path containment checks use raw string prefix tests. A sandbox base such as `/tmp/network-ai-sandbox` also matches a sibling path such as `/tmp/network-ai-sandbox_evil/secret.txt`.

An agent/user that can call `AgentRuntime.readFile()` or `AgentRuntime.listDir()` can read or list files outside the intended sandbox when the target path is in a sibling directory sharing the base path prefix. This breaks the documented sandbox boundary. Confirmed in Network-AI 5.12.1. Severity: Medium, CVSS 3.1 vector `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N`.

### Details
The vulnerable containment check is in `lib/agent-runtime.ts`:

```ts
resolvePath(filePath: string): string | null {
  const normalized = normalize(filePath);
  const absolute = isAbsolute(normalized)
    ? normalized
    : join(this.config.basePath, normalized);
  const resolved = resolve(absolute);

  // Traversal check
  if (!resolved.startsWith(this.config.basePath)) return null;
  return resolved;
}
```

`startsWith()` is not path-boundary-aware. If `this.config.basePath` is `/tmp/network-ai-sandbox`, then `/tmp/network-ai-sandbox_evil/secret.txt` also starts with `/tmp/network-ai-sandbox` despite being outside the sandbox.

The same pattern appears in `SandboxPolicy.isPathAllowed()` for allowed and blocked paths. `FileAccessor.read()`, `FileAccessor.write()`, and `FileAccessor.list()` rely on these checks before I/O, and `AgentRuntime.readFile()` exposes this behavior. Reads auto-approve by default when `autoApproveReads` is enabled.

Affected source evidence:

- `lib/agent-runtime.ts:393-423` — `isPathAllowed()` / `resolvePath()` use string `startsWith()` containment.
- `lib/agent-runtime.ts:669-691` — file read sink relies on those checks.
- `lib/agent-runtime.ts:933-958` — `AgentRuntime.readFile()` exposes file reads.

### PoC
Run from the repository root after installing dependencies:

```bash
node -r ts-node/register/transpile-only - <<'TS'
const { mkdtempSync, mkdirSync, writeFileSync, rmSync } = require('fs');
const { tmpdir } = require('os');
const { join } = require('path');
const { AgentRuntime } = require('./lib/agent-runtime');

(async () => {
  const parent = mkdtempSync(join(tmpdir(), 'network-ai-poc-'));
  const base = join(parent, 'sandbox');
  const sibling = join(parent, 'sandbox_evil');
  mkdirSync(base);
  mkdirSync(sibling);
  writeFileSync(join(sibling, 'secret.txt'), 'SECRET_OUTSIDE_SANDBOX', 'utf8');

  const runtime = new AgentRuntime({
    policy: { basePath: base, allowedPaths: ['.'], allowedCommands: [] },
  });

  const absoluteRead = await runtime.readFile(join(sibling, 'secret.txt'), 'poc-agent');
  const relativeRead = await runtime.readFile('../sandbox_evil/secret.txt', 'poc-agent');
  console.log(JSON.stringify({
    base,
    outside: join(sibling, 'secret.txt'),
    absoluteRead: { success: absoluteRead.success, content: absoluteRead.content },
    relativeRead: { success: relativeRead.success, content: relativeRead.content },
  }, null, 2));
  rmSync(parent, { recursive: true, force: true });
})();
TS
```

Observed result: both reads succeed and return `SECRET_OUTSIDE_SANDBOX`, even though the file is outside `basePath`.

### Impact
An agent/user with access to `AgentRuntime` file operations can bypass the intended sandbox root and read or list files outside the sandbox when those files are located in sibling paths sharing the sandbox base path prefix. This is a sandbox boundary bypass and path traversal vulnerability. Default confirmed impact is read/list disclosure. If an embedding application uses `FileAccessor.write()` directly or auto-approves runtime writes, the same root cause may allow writes outside the intended sandbox to prefix-collision sibling paths. No RCE chain was confirmed.


---

### Resolution (maintainer)

**Fixed in [v5.12.2](https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2) (commit `a59c13a`).** Install: `npm install network-ai@5.12.2` — published to npm with provenance.

`SandboxPolicy.resolvePath()` and `isPathAllowed()` now use separator-anchored prefix checks (`resolved === base || resolved.startsWith(base + path.sep)`) for both the allow-list and block-list. A sibling directory that merely shares a name prefix (e.g. `/srv/app-evil` vs base `/srv/app`) is no longer treated as in-scope.

All 3,269 tests pass against the patched build. Thanks to @sondt99 for the responsible disclosure.

## References
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-jvcm-f35g-w78p
- https://github.com/Jovancoding/Network-AI/commit/a59c13a1f0ce0e8a0779a90343eef92fac5ab4c3
- https://github.com/Jovancoding/Network-AI
- https://github.com/Jovancoding/Network-AI/releases/tag/v5.12.2
