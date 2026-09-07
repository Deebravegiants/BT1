# [H] npm PraisonAI SandboxExecutor allowedCommands bypass via shell chaining

## Summary
Severity: High
Advisory: GHSA-vjv9-7m7j-h833
CVE: CVE-2026-57136
CWE: CWE-693, CWE-78, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-vjv9-7m7j-h833
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=1.2.3 <1.7.2

## Details
## Summary

The published npm package `praisonai` exports `SandboxExecutor`, `CommandValidator`, and `sandboxExec` as "safe command execution with restrictions." When `allowedCommands` is configured, `CommandValidator` checks only the first whitespace-delimited token of the command string. `SandboxExecutor` then passes the entire original string to `spawn("sh", ["-c", command])`.

With a policy that allows only `echo`, this direct command is correctly rejected:

```sh
cat /tmp/marker
```

but this chained command is accepted and executed:

```sh
echo allowed; cat /tmp/marker
```

The shell executes `cat` even though `cat` is not allowlisted. This bypasses the command allowlist and can execute arbitrary shell commands with the PraisonAI process privileges when an application, CLI workflow, or agent pipeline exposes sandbox command execution to lower-trust users, prompts, or model output.

The PoV is deterministic and local-only. It creates and reads only a temporary marker file.

## Technical Details

In `src/praisonai-ts/src/cli/features/sandbox-executor.ts`, `CommandValidator.validate()` normalizes the command and authorizes only the first whitespace token:

```ts
const normalized = command.toLowerCase().trim();

if (this.allowedCommands) {
  const baseCmd = normalized.split(/\s+/)[0];
  if (!this.allowedCommands.includes(baseCmd)) {
    return { valid: false, reason: `Command '${baseCmd}' not in allowlist` };
  }
}
```

The denylist does not generally reject shell separators. It blocks a few specific patterns such as `; rm`, but not `; cat`, `&&`, `||`, backticks, `$()`, or newline as a general policy boundary.

`SandboxExecutor.spawn()` then executes the unmodified command string through a shell:

```ts
const proc = spawn('sh', ['-c', command], {
  cwd: this.config.cwd,
  env,
  timeout: this.config.timeout,
  stdio: ['pipe', 'pipe', 'pipe']
});
```

That creates a mismatch: the allowlist authorizes one command token, but the shell interprets the whole string as a script.

The published `npm:praisonai@1.7.1` dist files preserve the same behavior:

- `dist/cli/features/sandbox-executor.js` checks only `baseCmd`.
- `dist/cli/features/sandbox-executor.js` later invokes `spawn("sh", ["-c", command])`.
- `dist/index.js` exports `SandboxExecutor`, `CommandValidator`, and `sandboxExec`.

### Why This Is Not Intended Behavior

PraisonAI's sandbox docs describe sandbox execution as a security feature for AI-generated commands, with command validation, resource limits, path restrictions, network isolation, and execution isolation. The TypeScript source also describes this component as "Safe command execution with restrictions."

With `allowedCommands: ["echo"]`, PraisonAI correctly rejects `cat <marker>` when submitted directly. That proves the intended policy is to block non-allowlisted executables. The same policy allowing `echo allowed; cat <marker>` is therefore an authorization bypass, not merely a permissive configuration.

## PoV

Run from a local reproduction checkout:

```bash
node poc/pov_poc.js 1.7.1
```

Expected output includes:

```json
{
  "version": "1.7.1",
  "package": "npm:praisonai",
  "allowedCommands": ["echo"],
  "controls": {
    "directCatRejected": true,
    "benignEchoAllowed": true,
    "patchedControlRejectsChainedShell": true
  },
  "observed": {
    "directPolicy": {
      "allowed": false,
      "reason": "Command 'cat' not in allowlist"
    },
    "benignPolicy": {
      "allowed": true
    },
    "chainedPolicy": {
      "allowed": true
    },
    "chainedRun": {
      "success": true,
      "stdout": "allowed\npoc.7.1",
      "stderr": "",
      "exitCode": 0
    },
    "patchedControl": {
      "benign": {
        "allowed": true
      },
      "direct": {
        "allowed": false,
        "reason": "Command 'cat' not in allowlist"
      },
      "chained": {
        "allowed": false,
        "reason": "shell metacharacter rejected before execution"
      }
    }
  },
  "vulnerable": true
}
```

Interpretation:

- Direct `cat <marker>` is rejected by the allowlist.
- Benign `echo allowed` is accepted.
- `echo allowed; cat <marker>` is accepted by the same allowlist and executes the non-allowlisted `cat`.
- A patched-control validator that rejects shell metacharacters before execution blocks the chained command while still allowing benign `echo`.

The PoV installs `npm:praisonai@1.7.1` into a temporary project, creates a temporary marker file, and reads only that file. It does not contact any live service or execute destructive commands.

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

If lower-trust users, prompts, or model output can influence a command string sent to `SandboxExecutor` or `sandboxExec`, `allowedCommands` does not enforce the intended command boundary. An attacker can append arbitrary shell commands after an allowed first token and run them with the privileges of the PraisonAI process.

Concrete consequences depend on the hosting application and configured process privileges, but can include reading or modifying files, invoking local tools, using available credentials, or causing denial of service.

This report does not claim that npm PraisonAI exposes this as a default network service. It is a library-level sandbox/allowlist bypass in an exported TypeScript API that is explicitly designed for safe command execution.

### Severity

Suggested severity: High.

Rationale:

- `AV`: common deployment pattern is an application exposing agent prompts or command automation over a network.
- `AC`: attacker only needs to induce or submit a command string that starts with an allowed command.
- `PR`: conservative base score assumes the attacker can submit prompts or command requests to the application.
- `UI`: no operator action is needed once the command reaches the executor.
- `S`: impact is in the PraisonAI-hosting process.
- `C/I/A`: arbitrary shell commands can affect confidentiality, integrity, and availability depending on process privileges.

If maintainers score only local CLI use, `AV:L` may be reasonable. If they score public unauthenticated prompt or command endpoints built on this API, `PR:N` may be reasonable.

## Suggested Fix

Avoid passing policy-checked user strings to a shell.

Recommended:

1. Require callers to pass `{ command, args }`, or parse command strings into argv with a shell-aware parser.
2. Execute with `spawn(command, args, { shell: false })` / `execFile()` instead of `sh -c`.
3. Apply `allowedCommands` to the exact executable after normalization.
4. Reject shell metacharacters (`;`, `&&`, `||`, `|`, backticks, `$()`, newline, redirects) when a shell string API must be kept for compatibility.
5. Add regression tests proving `allowedCommands: ["echo"]` allows `echo ok` but rejects `cat marker`, `echo ok; cat marker`, `echo ok && cat marker`, and `echo ok | cat marker`.

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Package: `npm:praisonai`
- Component: TypeScript CLI feature `SandboxExecutor`
- Current head validated: `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`
- Current tag validated: `v4.6.58`
- Latest npm package validated: `1.7.1`

Suggested affected range:

```text
npm:praisonai >= 1.2.3, <= 1.7.1
```

Selected version sweep:

- `1.0.0`: package main cannot be required in the selected test environment.
- `1.2.0`, `1.2.1`, `1.2.2`: `SandboxExecutor` is not exported.
- `1.2.3`: vulnerable.
- `1.2.4`: vulnerable.
- `1.3.0`: vulnerable.
- `1.3.6`: vulnerable.
- `1.4.0`: vulnerable.
- `1.5.0`: vulnerable.
- `1.5.4`: vulnerable.
- `1.6.0`: vulnerable.
- `1.7.0`: vulnerable.
- `1.7.1`: vulnerable.

## Advisory History

This is distinct from known and previously submitted PraisonAI issues:

- `GHSA-r4f2-3m54-pp7q` covers PyPI `SubprocessSandbox` `shell=True` and blocklist bypass.
- `GHSA-2763-cj5r-c79m` covers PyPI `praisonai` OS command injection.
- `GHSA-v7px-3835-7gjx` covers PyPI `memory/hooks.py` shell injection.
- `GHSA-4wr3-f4p3-5wjh` covers Python agent tool approval allow-list manipulation.
- `GHSA-4mr5-g6f9-cfrh` covers PyPI/Python `execute_code` sandbox escape.
- `GHSA-9qhq-v63v-fv3j` covers an incomplete fix for a Python command injection.
- `GHSA-vmmj-pfw7-fjwp` covers npm `codeMode` host-process `new Function` sandbox escape.

No visible local or GitHub advisory covers npm TypeScript `SandboxExecutor`, `CommandValidator`, `allowedCommands`, or the first-token allowlist followed by `sh -c` shell-chaining root cause.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-vjv9-7m7j-h833
- https://github.com/MervinPraison/PraisonAI
