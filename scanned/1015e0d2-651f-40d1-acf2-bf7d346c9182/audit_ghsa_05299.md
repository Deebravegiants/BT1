# [H] npm PraisonAI utility shell safe-command wrapper allowlist bypass via shell chaining

## Summary
Severity: High
Advisory: GHSA-5jv7-2mjm-h6qj
CVE: CVE-2026-57133
CWE: CWE-693, CWE-78, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-5jv7-2mjm-h6qj
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=1.5.1 <1.7.2

## Details
## Summary

The published npm package `praisonai` ships `dist/tools/utility-tools.js`, which exports a `shell(command)` helper described in source as:

```text
Execute shell command (safe version - read-only commands)
```

The helper attempts to enforce a safe read-only command allowlist by checking only the first whitespace-delimited token:

```ts
const safeCommands = ['ls', 'cat', 'head', 'tail', 'wc', 'grep', 'find', 'echo', 'date', 'pwd', 'which'];
const firstWord = command.split(/\s+/)[0];

if (!safeCommands.includes(firstWord)) {
    return { success: false, error: `Command not allowed: ${firstWord}` };
}
```

It then passes the entire original string to Node `child_process.exec()`:

```ts
const { stdout, stderr } = await execAsync(command, { timeout: 5000 });
```

Because `exec()` runs the command through a shell, a command string that starts with an allowed command can append a second non-allowlisted command with shell metacharacters. For example, direct `printf <marker>` is rejected, but `echo ok; printf <marker>` is accepted and executes `printf`.

This bypasses the helper's safe-command policy and allows arbitrary shell commands to run with the PraisonAI process privileges when an application, agent, or integration exposes this helper to lower-trust users, prompts, model output, or plugin/tool input.

The PoV is deterministic and local-only. It installs only the npm package, runs harmless marker commands, and does not contact any live service after installation.

## Technical Details

`utility-tools.shell()` authorizes one token but executes the full shell string.

Source-head implementation:

```ts
export async function shell(command: string): Promise<ToolResult<string>> {
    // Only allow safe read-only commands
    const safeCommands = ['ls', 'cat', 'head', 'tail', 'wc', 'grep', 'find', 'echo', 'date', 'pwd', 'which'];
    const firstWord = command.split(/\s+/)[0];

    if (!safeCommands.includes(firstWord)) {
        return { success: false, error: `Command not allowed: ${firstWord}` };
    }

    try {
        const { exec } = await import('child_process');
        const { promisify } = await import('util');
        const execAsync = promisify(exec);

        const { stdout, stderr } = await execAsync(command, { timeout: 5000 });
        return { success: true, data: stdout || stderr };
    } catch (error: any) {
        return { success: false, error: error.message ?? String(error) };
    }
}
```

The published `npm:praisonai@1.7.1` dist file preserves the same behavior:

- `exports.shell = shell`
- `const firstWord = command.split(/\s+/)[0]`
- `if (!safeCommands.includes(firstWord)) ...`
- `const { stdout, stderr } = await execAsync(command, { timeout: 5000 })`

This creates a policy/parser differential: PraisonAI checks only the first token, while the shell parses the full string as a script.

### Why This Is Not Intended Behavior

The helper is explicitly documented in code as a "safe version" for read-only commands and contains an allowlist of specific safe commands. The control test proves that non-allowlisted commands are intended to be blocked: direct `printf <marker>` returns `Command not allowed: printf`.

The same helper accepting `echo ok; printf <marker>` is therefore a bypass of the intended safe-command boundary, not merely a permissive command runner.

This is also consistent with Node's own guidance for shell execution: `child_process.exec()` runs through a shell, and shell metacharacters can change which commands execute. The fix should make PraisonAI's authorization boundary match what is actually executed.

## PoV

Run from a local reproduction checkout:

```bash
node poc/pov_poc.js 1.7.1
```

Observed output summary from `evidence/pov-npm-1.7.1.json`:

```json
{
  "package": "npm:praisonai",
  "version": "1.7.1",
  "installedPackageVersion": "1.7.1",
  "commands": {
    "directDisallowedCommand": "printf poc.7.1",
    "benignAllowedCommand": "echo poc",
    "chainedBypassCommand": "echo poc; printf poc.7.1"
  },
  "controls": {
    "directDisallowedRejected": true,
    "benignAllowedAccepted": true,
    "patchedControlRejectsChainedShell": true
  },
  "observed": {
    "directDisallowed": {
      "success": false,
      "error": "Command not allowed: printf"
    },
    "chainedBypass": {
      "success": true,
      "data": "poc\npoc.7.1"
    }
  },
  "vulnerable": true
}
```

Interpretation:

- Direct `printf <marker>` is rejected because `printf` is not in `safeCommands`.
- Benign `echo ...` is accepted.
- `echo ...; printf <marker>` is accepted because the first token is `echo`.
- The shell then executes the non-allowlisted `printf` command.
- A patched-control validator that rejects shell metacharacters before execution blocks the chained command while still allowing benign `echo`.

The PoV uses only harmless marker output. It does not read system files, leak environment variables, call external services, or run destructive commands.

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

If lower-trust users, prompts, model output, plugins, or tool input can influence a command string passed to `utility-tools.shell()`, the safe-command allowlist does not restrict execution to the intended read-only commands. An attacker can append arbitrary shell commands after an allowed first token and run them with the PraisonAI process privileges.

Concrete consequences depend on the embedding application and process privileges, but can include:

- reading files and secrets available to the process;
- modifying files or project state;
- invoking local tools and package managers;
- network exfiltration if the host permits egress; and
- denial of service by running expensive commands.

This report does not claim that npm PraisonAI exposes this helper as a default unauthenticated network service. It is a library-level safe-command wrapper bypass in a shipped npm subpath.

### Severity

Suggested severity: High.

Rationale:

- `AV`: common PraisonAI use is a network-facing application, agent API, or tool integration that accepts user or prompt-controlled tasks.
- `AC`: a single command string beginning with an allowed command is sufficient.
- `PR`: conservative scoring assumes the attacker can submit prompts or work items to the application using this helper.
- `UI`: no further operator interaction is required once the command reaches the helper.
- `S`: impact is within the PraisonAI-hosting process and its host context.
- `C/I/A`: arbitrary shell commands can affect confidentiality, integrity, and availability depending on process privileges.

If maintainers score only direct local library use, `AV:L` may be reasonable. If a deployment exposes this helper through unauthenticated agent/tool endpoints, `PR:N` may be reasonable.

## Suggested Fix

Avoid passing policy-checked strings to a shell.

Recommended:

1. Replace `exec(command)` with `execFile()` or `spawn(command, args, { shell: false })`.
2. Require callers to pass `{ command, args }` instead of a shell string, or parse the shell string into argv with a shell-aware parser before policy checks.
3. Apply the allowlist to the exact executable that will be invoked.
4. Reject shell metacharacters (`;`, `&&`, `||`, `|`, backticks, `$()`, redirects, newlines) if a string API must remain available.
5. Add regression tests proving that `echo ok` is allowed while `printf marker`, `echo ok; printf marker`, `echo ok && printf marker`, and `echo ok | printf marker` are rejected.

If this helper is not intended to be public, also consider adding a package `exports` map that exposes only supported public API paths.

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Ecosystem: `npm`
- Package: `praisonai`
- Component: TypeScript utility tools helper `src/praisonai-ts/src/tools/utility-tools.ts`
- Published dist path: `node_modules/praisonai/dist/tools/utility-tools.js`
- Latest npm package validated: `1.7.1`
- Current `origin/main` validated: `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`
- `src/praisonai-ts/package.json` at `origin/main`: `praisonai` `1.7.1`

Suggested affected range:

```text
npm:praisonai >= 1.5.1, <= 1.7.1
```

All published npm `1.x` versions were swept locally:

- `1.0.0` through `1.5.0`: `dist/tools/utility-tools.js` was not present in the tested package.
- `1.5.1`, `1.5.2`, `1.5.3`, `1.5.4`, `1.6.0`, `1.7.0`, and `1.7.1`: vulnerable.

The npm package has no `exports` map and ships `dist` in its `files` list, so the affected helper is importable as a package subpath:

```js
const { shell } = require("praisonai/dist/tools/utility-tools.js");
```

The root package entry point does not appear to re-export this helper directly. This report is scoped to the shipped npm subpath and the TypeScript source that generates it.

## Advisory History

Visible PraisonAI advisories and prior submissions were checked. The closest known issues are adjacent but distinct:

- `GHSA-vjv9-7m7j-h833` covers npm TypeScript `SandboxExecutor.allowedCommands` in `src/cli/features/sandbox-executor.ts`, where a caller-supplied allowlist is checked before `spawn("sh", ["-c", command])`.
- This report covers npm TypeScript `utility-tools.shell()` in `src/tools/utility-tools.ts`, where a built-in "safe read-only commands" allowlist is checked before `child_process.exec(command)`.
- Fixing only `SandboxExecutor` leaves this helper unchanged.
- The public Python/PyPI command-injection advisories cover different packages, files, and execution paths, such as Python `execute_command`, `run_python()`, memory hooks, and subprocess sandbox code.

This is a sibling-callsite variant of the same mature allowlist/shell-parser class, but it is not the same function, policy surface, affected version range, or shipped import path as the prior npm `SandboxExecutor` advisory.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-5jv7-2mjm-h6qj
- https://github.com/MervinPraison/PraisonAI
