# [C] NodeVM builtin denylist bypass via process and inspector/promises allows host code execution

## Summary
Severity: Critical
Advisory: GHSA-rp36-8xq3-r6c4
CVE: CVE-2026-47140
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-rp36-8xq3-r6c4
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.4

## Details
## Summary

`NodeVM` blocks several dangerous Node.js builtins such as `module`, `worker_threads`, `cluster`, `vm`, `repl`, and `inspector`.

However, the denylist misses `process` and `inspector/promises`. Both can be used from sandboxed code to reach host-side execution primitives.

This allows sandboxed code to bypass the intended builtin restrictions and execute code in the host process.

## Details

The dangerous builtin denylist is defined in `lib/builtin.js`. This list does not include:

```text
process
inspector/promises
```

Non-denied builtins are exposed to the sandbox through:

```js
builtins.set(key, special ? special : vm => vm.readonly(hostRequire(key)));
```

Because of this, sandboxed code can bypass the expected restrictions in two ways:

1. `require('process').getBuiltinModule('child_process')` reloads `child_process`, even when `child_process` is excluded.
2. `require('inspector/promises')` exposes the Inspector protocol and can call `Runtime.evaluate` in the host process.

## PoC

Tested on:

```text
vm2: 3.11.2
Node.js: v25.9.0
```

Run from the vm2 repository root:

```bash
node poc/dangerous-builtin-denylist-rce.js
```
[dangerous-builtin-denylist-rce.js](https://github.com/user-attachments/files/27570113/dangerous-builtin-denylist-rce.js)


The PoC first confirms the intended restrictions work:

```text
require("inspector"): BLOCKED
require("child_process"): BLOCKED
```

Then it bypasses them:

```text
require("process").getBuiltinModule("child_process").execFileSync(...)
```

This spawns a host child process. It also confirms:

```text
require("inspector/promises").Session().post("Runtime.evaluate", ...)
```

This evaluates JavaScript in the host process.

<img width="858" height="766" alt="Screenshot 2026-05-10 at 11 53 33 AM" src="https://github.com/user-attachments/assets/7614aecb-5ffd-4c41-bfe8-e1fcb3b1bb59" />

## Impact

An attacker who can run untrusted JavaScript inside `NodeVM` with affected builtin settings can escape the sandbox and execute arbitrary code in the host process.

This can lead to full compromise of the application process, including reading files, writing files, spawning processes, and accessing host environment secrets.

(This is not reachable with the default NodeVM configuration where require is disabled or no affected builtins are allowed. It affects applications that allow process, inspector/promises, or the wildcard "*" in require.builtin.)

## Suggested fix

Add `process` and `inspector/promises` to the dangerous builtin blocklist.

Also consider blocking dangerous builtin families by prefix, for example blocking both:

```text
inspector
inspector/*
```

instead of only exact module names.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-rp36-8xq3-r6c4
- https://nvd.nist.gov/vuln/detail/CVE-2026-47140
- https://github.com/patriksimek/vm2/commit/a1ed47a98d1cc36cb48c0d566d55889688e0b59b
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
