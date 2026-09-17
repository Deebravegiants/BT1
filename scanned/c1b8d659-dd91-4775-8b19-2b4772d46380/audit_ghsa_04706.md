# [C] npm PraisonAI codeMode sandbox escape via Function constructor

## Summary
Severity: Critical
Advisory: GHSA-vmmj-pfw7-fjwp
CVE: CVE-2026-57138
CWE: CWE-184, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-vmmj-pfw7-fjwp
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=1.4.0 <1.7.2

## Details
## Summary

The published npm package `praisonai` exports a TypeScript built-in tool named `codeMode`. The package describes this tool as executing code in a sandboxed environment, marks its capability as `sandbox: true`, and registers it through the public tools facade.

The implementation does not create an isolation boundary. It applies a small regular-expression blocklist, sets `process` and `require` to `undefined` inside a plain JavaScript object, and then executes attacker-controlled code with the host process `new Function` constructor:

```text
const fn = new Function('sandbox', `with (sandbox) { ${code} }`);
const result = fn(sandbox);
```

Because this runs in the host V8 context, code inside `codeMode` can use the JavaScript prototype chain to recover the real `Function` constructor:

```text
({}).constructor.constructor('return process')()
```

From a normal CommonJS application script, the recovered `process` object exposes `process.mainModule.require`. That bypasses the explicit `require('fs')` and `require('child_process')` controls and allows host filesystem access and subprocess execution from code that was supposed to be sandboxed.

## Technical Details

Current-head source says `codeMode` is a built-in package tool and explicitly advertises a sandbox boundary:

```text
src/praisonai-ts/src/tools/builtins/code-mode.ts
  13: description: 'Execute code that can import and use other tools in a sandboxed environment',
  24: capabilities: {
  25:   sandbox: true,
  26:   code: true,
  28: packageName: 'praisonai',
  85: description: 'Execute code in a sandboxed environment with access to imported tools. Write files, run code, and get results.',
```

The same file implements security as a blocklist of exact source-code patterns:

```text
src/praisonai-ts/src/tools/builtins/code-mode.ts
  108: const blockedPatterns = [
  109:   /require\s*\(\s*['"]child_process['"]\s*\)/,
  110:   /require\s*\(\s*['"]fs['"]\s*\)/,
  111:   /import\s+.*from\s+['"]child_process['"]/,
  112:   /process\.exit/,
  113:   /eval\s*\(/,
```

It then tries to hide dangerous globals by shadowing names in a normal object:

```text
src/praisonai-ts/src/tools/builtins/code-mode.ts
  168: process: undefined,
  169: require: undefined,
```

Finally, it executes the untrusted code in the host process using `new Function` and `with (sandbox)`:

```text
src/praisonai-ts/src/tools/builtins/code-mode.ts
  187: const fn = new Function(
  188:   'sandbox',
  189:   `with (sandbox) { ${code} }`
  190: );
  191: const result = fn(sandbox);
```

This is not a sandbox. `new Function` does not create a separate security context, and variable shadowing does not remove access to constructors reachable through normal JavaScript objects.

The tool is reachable through the public npm SDK:

```text
src/praisonai-ts/src/index.ts
  117: airweaveSearch, codeMode,

src/praisonai-ts/src/tools/tools.ts
  104: // Code Mode
  105: registry.register(CODE_MODE_METADATA, createCodeModeTool as ToolFactory);
  167: // Code Mode
  168: codeMode: (config?: CodeModeConfig) => codeMode(config),
```

### Why This Is Not Intended Behavior

This is not merely "the user can execute code because codeMode executes code." The vulnerability is that code which is explicitly described and exposed as sandboxed can escape the intended restrictions.

The implementation itself proves an intended security boundary exists:

- `CODE_MODE_METADATA.capabilities.sandbox` is `true`;
- the tool description says it executes in a sandboxed environment;
- direct access to `fs` and `child_process` is explicitly blocked;
- `process` and `require` are explicitly shadowed as `undefined`;
- `allowNetwork` defaults to `false`; and
- the config includes security-relevant controls such as `blockedTools`, `allowedPaths`, `timeoutMs`, and `maxMemoryMb`.

The PoV shows those intended restrictions work for naive payloads but fail for a standard JavaScript prototype-chain escape.

PraisonAI's official JavaScript and TypeScript docs describe the npm package as a production-ready agent framework installed with `npm install praisonai`. Public PraisonAI advisories rate comparable Python sandbox escapes as Critical when user/LLM-supplied code crosses from a claimed sandbox into host execution.

## PoV

The PoV installs a published npm package version into a temporary project and runs from a real CommonJS script file. Running from a file is important because normal Node applications expose `process.mainModule.require`; `node -e` or stdin do not always reproduce that deployment shape.

Run from a local reproduction checkout:

```fish
node poc/pov_poc.js 1.7.1
```

Observed result:

```json
{
  "package": "praisonai",
  "version": "1.7.1",
  "codeModeExported": true,
  "directRequireFsControl": {
    "stderr": "Blocked pattern detected: require\\s*\\(\\s*['\"]fs['\"]\\s*\\)",
    "exitCode": 1,
    "success": false,
    "error": "Code contains blocked patterns for security"
  },
  "directChildProcessControl": {
    "stderr": "Blocked pattern detected: require\\s*\\(\\s*['\"]child_process['\"]\\s*\\)",
    "exitCode": 1,
    "success": false,
    "error": "Code contains blocked patterns for security"
  },
  "escapedProcessEnv": {
    "output": "poc",
    "exitCode": 0,
    "success": true
  },
  "escapedFilesystem": {
    "output": "fs-ok",
    "exitCode": 0,
    "success": true
  },
  "escapedCommand": {
    "output": "poc",
    "exitCode": 0,
    "success": true
  }
}
```

Interpretation:

- direct `require('fs')` is blocked;
- direct `require('child_process')` is blocked;
- the Function-constructor payload recovers host `process`;
- the escaped process reads a host environment variable;
- the escaped process imports `fs`; and
- the escaped process imports `child_process` and runs a harmless `printf`.

The PoV does not contact any LLM provider or external service after npm package installation. It does not modify host files or execute a destructive command.

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

An attacker who can supply code to `codeMode` can escape the advertised sandbox and execute with the privileges of the Node.js PraisonAI process.

Realistic entry points include:

- an application that exposes `codeMode` as an agent tool to end users;
- an LLM/tool-call flow where prompt-controlled content reaches the `code` parameter;
- MCP or tool-registry integrations that make the built-in `codeMode` tool callable; or
- any multi-tenant service that relies on `codeMode` to safely run user or model-generated JavaScript.

Impact after escape includes:

- reading process environment variables, including API keys and service tokens;
- reading files available to the Node process;
- spawning subprocesses with `child_process`;
- writing or modifying files through host filesystem APIs; and
- terminating or resource-exhausting the host process.

### Severity

Suggested severity: Critical.

Rationale:

- `AV`: `codeMode` is a designated agent/tool surface and can be reached over the network in standard agent applications that expose tool calls to users or LLM-controlled workflows.
- `AC`: a single code payload is enough.
- `PR`: the attacker needs the ability to submit code or prompt-controlled content to an agent/tool flow.
- `UI`: no additional user interaction is required once the tool is invoked.
- `S`: execution crosses from the advertised sandbox security scope into the host Node.js process.
- `C`: host files and environment variables are readable.
- `I`: host subprocess and filesystem APIs are reachable.
- `A`: escaped code can terminate processes or consume host resources.

## Suggested Fix

Do not use host-process `new Function` plus source-code blocklists as a sandbox.

Recommended fix direction:

1. Disable or clearly mark npm `codeMode` as unsafe until a real isolation boundary exists.
2. Execute untrusted code in a separate OS process, container, worker isolate, or similar boundary with a restricted user, minimal environment, temporary working directory, no inherited secrets, and explicit IPC for allowed tool calls.
3. Enforce `allowNetwork`, `allowedPaths`, `timeoutMs`, `maxMemoryMb`, `allowedTools`, and `blockedTools` at that boundary instead of by scanning source strings.
4. Do not rely on `node:vm` alone for untrusted code. The Node.js documentation explicitly says the `vm` module is not a security mechanism.
5. Add regression tests for:
   - direct `require('fs')` and `require('child_process')` blocked controls;
   - `({}).constructor.constructor('return process')()` blocked;
   - `process.mainModule.require('fs')` unavailable;
   - `process.mainModule.require('child_process')` unavailable;
   - host environment variables unavailable unless explicitly passed; and
   - tool-call IPC still works for allowed tools.

If maintainers need an emergency mitigation before a real sandbox exists, reject `codeMode` execution unless the caller opts into "unsafe host JS execution" with clear documentation that it can access the full Node process.

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Ecosystem: `npm`
- Package: `praisonai`
- Component: `src/praisonai-ts/src/tools/builtins/code-mode.ts`
- Current npm version checked: `1.7.1`
- Refreshed `origin/main` checked: `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`

Confirmed affected range:

```text
>= 1.4.0, <= 1.7.1
```

Boundary:

```text
1.3.6 does not export codeMode and does not ship dist/tools/builtins/code-mode.js.
```

No fixed npm version is known at the time of this report.

### Version Sweep

The included sweep installs selected npm versions and runs the same vulnerable shape from a script file:

```fish
node poc/version_sweep_poc.js
```

Observed result:

```text
1.3.6: codeModeExported=false, hasDistCodeMode=false
1.4.0: directRequireFsBlocked=true, escapeProcessEnv=true, escapeFilesystem=true, escapeCommand=true
1.5.4: directRequireFsBlocked=true, escapeProcessEnv=true, escapeFilesystem=true, escapeCommand=true
1.6.0: directRequireFsBlocked=true, escapeProcessEnv=true, escapeFilesystem=true, escapeCommand=true
1.7.0: directRequireFsBlocked=true, escapeProcessEnv=true, escapeFilesystem=true, escapeCommand=true
1.7.1: directRequireFsBlocked=true, escapeProcessEnv=true, escapeFilesystem=true, escapeCommand=true
```

Git history for the TypeScript file points to the 1.4.0 integration:

```text
56f36e25 feat: bump version to 1.4.0 and add AI SDK integration dependencies
2bad9a50 feat: bump version to 1.4.0 and add AI SDK integration dependencies
```

## Advisory History

Checked:

- visible PraisonAI advisories and prior reports;
- public GitHub advisory search results for PraisonAI `codeMode`, npm, sandbox, `new Function`, `process`, and `child_process`; and
- visible public PraisonAI advisories for sandbox escapes.

Closest related advisories are Python/PyPI scoped and do not cover this npm TypeScript implementation:

- `GHSA-qf73-2hrx-xprp` / `CVE-2026-39888`: `pip:praisonaiagents` `execute_code()` frame traversal in a Python subprocess sandbox.
- `GHSA-4mr5-g6f9-cfrh` / `CVE-2026-47392`: `pip:praisonai` Python `execute_code()` sandbox escape through `print.__self__`.
- Other published PraisonAI sandbox advisories cover Python `execute_code`, `SubprocessSandbox`, Sandlock/native fallback, or CLI/managed-agent bridges.

This report is distinct because it targets:

- ecosystem: `npm`;
- package: `praisonai`;
- component: `src/praisonai-ts/src/tools/builtins/code-mode.ts`;
- root cause: host-context `new Function` plus blocklist/name-shadowing sandbox; and
- affected range: `>= 1.4.0, <= 1.7.1`.

One private npm report has already been submitted for TypeScript `AgentOS` missing authentication (`GHSA-9752-mhqh-h34f`). That is also distinct: it covers unauthenticated HTTP agent listing/invocation, not a `codeMode` sandbox escape.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-vmmj-pfw7-fjwp
- https://github.com/MervinPraison/PraisonAI
