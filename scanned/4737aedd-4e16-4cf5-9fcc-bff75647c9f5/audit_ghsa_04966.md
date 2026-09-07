# [H] npm PraisonAI SandboxExecutor network-isolated mode does not block non-proxy-aware network clients

## Summary
Severity: High
Advisory: GHSA-gqmf-56h7-rrpf
CVE: CVE-2026-57135
CWE: CWE-653, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-gqmf-56h7-rrpf
Type: github-advisory

## Affected
- npm: `praisonai` — affected >=1.2.3 <1.7.2

## Details
## Summary

The published npm package `praisonai` exports a TypeScript `SandboxExecutor` with a `network-isolated` mode. The CLI lists that mode as:

```text
network-isolated  No network access (proxy blocked)
```

The implementation does not create a network namespace, firewall rule, socket filter, or proxy-enforced execution boundary. It only injects proxy environment variables into the child process:

```ts
http_proxy: 'http://localhost:0',
https_proxy: 'http://localhost:0',
HTTP_PROXY: 'http://localhost:0',
HTTPS_PROXY: 'http://localhost:0',
no_proxy: '',
NO_PROXY: ''
```

Clients that do not explicitly honor those proxy variables continue to use the host network stack. A local-only PoV shows that, inside `mode: "network-isolated"`, a proxy-aware Node invocation is stopped, while a plain Node HTTP client reaches a loopback HTTP server from the same sandboxed command environment.

This is a network-isolation protection failure in an exported npm API and CLI mode. It is not a generic claim that every PraisonAI sandbox backend is affected.

## Technical Details

`src/praisonai-ts/src/cli/features/sandbox-executor.ts` declares the mode:

```ts
export type SandboxMode = 'disabled' | 'basic' | 'strict' | 'network-isolated';
```

`SandboxExecutor.spawn()` starts the command through the host shell and passes only the environment returned by `buildEnv()`:

```ts
const proc = spawn('sh', ['-c', command], {
  cwd: this.config.cwd,
  env,
  timeout: this.config.timeout,
  stdio: ['pipe', 'pipe', 'pipe']
});
```

For `network-isolated`, `buildEnv()` does not apply an OS-level network restriction. It only sets proxy variables:

```ts
case 'network-isolated':
  // No network access (requires additional OS-level setup)
  return {
    ...baseEnv,
    http_proxy: 'http://localhost:0',
    https_proxy: 'http://localhost:0',
    HTTP_PROXY: 'http://localhost:0',
    HTTPS_PROXY: 'http://localhost:0',
    no_proxy: '',
    NO_PROXY: ''
  };
```

The CLI mode listing presents this as no network access:

```ts
'network-isolated': 'No network access (proxy blocked)'
```

That creates a false boundary. Proxy variables affect only clients that choose to read and honor them. Other clients can still open sockets directly from the child process.

### Why This Is Not Intended Behavior

The vulnerable behavior is not "commands can run." The issue is that a mode named `network-isolated` and displayed to users as "No network access" still allows direct socket access.

The source comment says `network-isolated` requires additional OS-level setup, which is consistent with the finding: proxy variables alone are not a network isolation mechanism. The exported npm API and CLI mode do not provide such setup or warn callers that this mode is only a best-effort proxy hint.

If the intended behavior is merely "set proxy variables for cooperative clients," the mode name and CLI description should be changed so users do not rely on it as a security boundary.

## PoV

Run from a local reproduction checkout:

```bash
node poc/pov_poc.js 1.7.1
```

The PoV:

1. Installs `npm:praisonai@1.7.1` into a temporary project.
2. Starts a harmless HTTP server bound to `127.0.0.1` on a random local port.
3. Creates `new SandboxExecutor({ mode: "network-isolated" })`.
4. Confirms the child environment contains the proxy variables.
5. Runs `node --use-env-proxy client.js` as a proxy-aware control. It fails and does not reach the server.
6. Runs `node client.js` without proxy opt-in. It reaches the server and prints the marker.

Observed output summary from `evidence/pov-npm-1.7.1.json`:

```json
{
  "version": "1.7.1",
  "mode": "network-isolated",
  "control": {
    "localServerBoundToLoopback": true,
    "proxyVariablesSet": true,
    "proxyAwareClientStopped": true,
    "requestReachedLoopbackServer": true
  },
  "observed": {
    "proxyAwareRun": {
      "success": false,
      "stdout": "",
      "exitCode": 2
    },
    "netRun": {
      "success": true,
      "stdout": "BODY=poc\n",
      "exitCode": 0
    },
    "loopbackHitCount": 1
  },
  "vulnerable": true
}
```

The PoV is local-only. It does not contact any external host after npm package installation, and it does not use cloud metadata or destructive commands.

## PoC

The PoV section above contains the local reproduction command, input, and decisive output.

## Impact

Applications often use sandbox network controls to prevent prompt-injected, user-supplied, or model-generated commands from exfiltrating secrets or reaching internal services. A caller who relies on `network-isolated` mode for that boundary can still get network egress by using any client that ignores proxy environment variables or by using direct socket APIs.

Depending on the hosting environment, this can allow:

- exfiltration from commands that can read local files, process output, or inherited environment variables;
- access to localhost or internal network services reachable from the PraisonAI host;
- requests to cloud metadata or service endpoints if the host network permits them; and
- bypass of application policy that allows command execution only under a no-network assumption.

This report does not claim that npm PraisonAI exposes this as an unauthenticated network service by default. It is a library-level isolation bypass in an exported TypeScript API and CLI mode.

### Severity

Suggested severity: High.

Rationale:

- `AV`: common use is a network-facing application or agent service that accepts user or prompt-controlled work and executes it through the sandbox.
- `AC`: a single command using a non-proxy-aware network client is sufficient.
- `PR`: conservative scoring assumes the attacker can submit prompts or work items to the application using PraisonAI.
- `UN`: no additional operator interaction is required once the command is executed.
- `S`: impact is scored against the PraisonAI-hosting process and its network privileges.
- `C`: network egress can allow data exfiltration from the sandboxed command context.
- `I/A`: reachable internal services can receive attacker-controlled requests, with impact depending on deployment.

If maintainers score only local CLI use, `AV:L` may be appropriate. If a deployment exposes this through unauthenticated agent endpoints, `PR:N` may be appropriate.

## Suggested Fix

Do not represent proxy environment variables as network isolation.

Recommended:

1. For a true `network-isolated` mode, run commands inside an execution boundary with OS-enforced network denial, such as a network namespace, firewall rule, sandbox profile, container, VM, or platform-specific socket filter.
2. Add regression tests that start a loopback server and verify that direct socket clients, Node `http.get`, Python sockets, `curl`, and other common clients cannot connect under `network-isolated`.
3. If only proxy hints are intended, rename the mode to something like `proxy-blocked`, document that it is not a security boundary, and keep "network-isolated" unavailable until OS-level enforcement exists.
4. Consider default-deny egress with explicit allowlists for destinations that must remain reachable from sandboxed commands.

## Affected Package/Versions

- Repository: `MervinPraison/PraisonAI`
- Ecosystem: `npm`
- Package: `praisonai`
- Component: TypeScript CLI feature `SandboxExecutor`
- Latest npm package validated: `1.7.1`
- Current `origin/main` validated: `1ad58ca02975ff1398efeda694ea2ab78f20cf3e`
- `src/praisonai-ts/package.json` at `origin/main`: `praisonai` `1.7.1`

Suggested affected range:

```text
npm:praisonai >= 1.2.3, <= 1.7.1
```

Selected version sweep:

- `1.0.0`: package main cannot be required in the selected test environment.
- `1.0.19`, `1.1.0`, `1.2.0`, `1.2.1`, `1.2.2`: `SandboxExecutor` is not exported.
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

Visible PraisonAI advisories and prior submissions were checked. The closest related findings are distinct:

- `GHSA-r4f2-3m54-pp7q` covers PyPI `SubprocessSandbox` `shell=True` and blocklist bypass.
- `GHSA-6jcq-6546-qrrw` covers Python Sandlock fallback to unrestricted subprocess execution when native Landlock is unavailable.
- `GHSA-vmmj-pfw7-fjwp` covers npm `codeMode` host-process `new Function` sandbox escape.
- `GHSA-vjv9-7m7j-h833` covers npm `SandboxExecutor` `allowedCommands` bypass through shell chaining.

This report is narrower and distinct: npm TypeScript `SandboxExecutor` `network-isolated` mode advertises no network access but enforces only proxy environment variables, so non-proxy-aware clients keep network access without needing shell chaining or a disallowed executable.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-gqmf-56h7-rrpf
- https://github.com/MervinPraison/PraisonAI
