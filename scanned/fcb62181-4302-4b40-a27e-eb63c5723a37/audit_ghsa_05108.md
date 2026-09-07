# [M] js-toml has silent type confusion via falsy-primitive duplicate-key bypass

## Summary
Severity: Medium
Advisory: GHSA-m34p-749j-x6m6
CVE: CVE-2026-50029
CWE: CWE-697
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-m34p-749j-x6m6
Type: github-advisory

## Affected
- npm: `js-toml` — affected >=0 <1.1.2

## Details
### Summary

`js-toml`'s interpreter checks whether a key already exists in a parser-built container with `if (object[key])` instead of `if (key in object)`. When the prior value is a falsy primitive — `false`, `0`, `0n`, `0.0`, `-0`, or `""` — the duplicate-key branch is skipped and the value is silently overwritten by a later sub-table, dotted-key sub-table, or array-of-tables sharing the same name. Per the TOML 1.0.0 spec ("Defining a key multiple times is invalid"; "You cannot define any key or table more than once"), this should be a parse error.

The result is **structural type confusion of attacker-named keys** in the value returned by `load()`. A boolean-typed `false` (or numeric `0`) becomes a truthy object. Host applications that gate behavior on `if (config.flag)`, `if (!user.banned)`, `if (config.allowDelete)`, or `if (config.publicMode)` will silently take the truthy branch.

This is **distinct** from [GHSA-65fc-cr5f-v7r2](https://github.com/sunnyadn/js-toml/security/advisories/GHSA-65fc-cr5f-v7r2) (the 1.0.2 prototype-pollution fix). `Object.prototype` is **not** polluted. The `Object.create(null)` mitigation from 1.0.2 is intact; the bug here is in the duplicate-key state machine, not in container construction.

### Details

Two truthy checks are wrong:

`src/load/interpreter.ts:214` — `Interpreter.tryCreatingObject`

```js
if (object[key]) {            // falsy primitives slip through
    // duplicate-key logic
} else {
    object[key] = createSafeObject();   // silently overwrites the prior falsy value
    ...
}
```

`src/load/interpreter.ts:278` — `Interpreter.getOrCreateArray`

```js
if (object[first] && !Array.isArray(object[first])) {   // same flaw
    throw new DuplicateKeyError();
}
object[first] = object[first] || [];   // overwrites the prior falsy value
```

Both should use the `in` operator. Containers are created via `Object.create(null)`, so `in` is unambiguous (no inherited keys to worry about).

The bug is reachable through every parent-walking interpreter path:

- `assignValue` — dotted keys in `key = value`
- `createTable` — `[stdTable]` headers
- `getOrCreateArray` — `[[arrayOfTables]]` headers

### PoC

```toml
isAdmin = false
[isAdmin]
forced = "yes"
```

```js
import { load } from 'js-toml';

const config = load(`
isAdmin = false
[isAdmin]
forced = "yes"
`);

console.log(JSON.stringify(config));
// {"isAdmin":{"forced":"yes"}}

console.log(config.isAdmin ? 'BYPASS' : 'safe');
// BYPASS

if (config.isAdmin) {
  // attacker reaches admin-only code
}
```

### Impact

Spec-violating input acceptance leading to structural type confusion. (CWE-697)

### Suggested fix

in `src/load/interpreter.ts`

```diff
export class Interpreter extends BaseCstVisitor {
     ignoreImplicitDeclared,
     ignoreExplicitDeclared
   ) {
-    if (object[key]) {
+    if (key in object) {
       if (
         !isPlainObject(object[key]) ||
         (!ignoreExplicitDeclared &&
```
```diff
export class Interpreter extends BaseCstVisitor {
       return this.getOrCreateArray(keys, object[first], idx + 1);
     }

-    if (object[first] && !Array.isArray(object[first])) {
+    if (first in object && !Array.isArray(object[first])) {
       throw new DuplicateKeyError();
     }

     object[first] = object[first] || [];
```

## References
- https://github.com/sunnyadn/js-toml/security/advisories/GHSA-m34p-749j-x6m6
- https://github.com/sunnyadn/js-toml/commit/e0504fa5d3dcde2d1d588c9001c24b7b700beeeb
- https://github.com/sunnyadn/js-toml
- https://github.com/sunnyadn/js-toml/releases/tag/v1.1.2
