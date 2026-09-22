# [H] parse-nested-form-data has Prototype Pollution via `__proto__` in FormData field names

## Summary
Severity: High
Advisory: GHSA-xp7r-j8r6-j9h3
CVE: CVE-2026-45302
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-xp7r-j8r6-j9h3
Type: github-advisory

## Affected
- npm: `parse-nested-form-data` — affected >=0 <1.0.1

## Details
## Summary

`parseFormData()` walks bracket and dot-notation FormData field names into nested objects without filtering reserved property keys. A single FormData field whose name begins with `__proto__`, or contains `.__proto__.` mid-path, causes the parser to traverse onto `Object.prototype` and assign properties there, polluting the prototype chain of every plain object in the running process.

## Details

The vulnerability is in `handlePathPart` in `src/index.ts`, which performs `currentObject[pathPart.path]` and `currentObject[pathPart.path] = val` for object-type path segments without rejecting reserved keys. When the segment is `__proto__`, the read returns `Object.prototype`, which then becomes the next traversal target, and the next assignment lands on the prototype.

Reproduction on a fresh install of `parse-nested-form-data@1.0.0`:

```js
import { parseFormData } from 'parse-nested-form-data';
const fd = new FormData();
fd.append('__proto__.polluted', 'yes');
parseFormData(fd);
console.log(({}).polluted); // -> 'yes'
console.log(([]).polluted); // -> 'yes'
```

Equivalent vectors:

- `__proto__[polluted]=yes`
- `a.__proto__.polluted=yes` (mid-path traversal)
- `a[0].__proto__.polluted=yes` (mid-path through an array element)

`constructor.prototype.x` was incidentally blocked by an existing duplicate-key guard (because `Object` is a function and failed the JSON-object check), but relying on that was fragile, so the fix denylists `constructor` and `prototype` as well as `__proto__`. The array branch (`a[0]`, `a[]`) was not exploitable in practice - the regex restricts array-index segments to digit characters - but the forbidden-key check is applied before the object/array type branching as defense in depth, so any future change to the regex cannot reintroduce the issue.

## Impact

Any application that passes attacker-controlled `FormData` (or any `Iterable<[string, string | File]>`) to `parseFormData()` - typically an HTTP server processing form submissions - allows an unauthenticated remote client to mutate `Object.prototype` of the running process via a single field name. Concrete consequences depend on the host application and may include corrupted application state, altered control flow in code that reads ambient properties off objects, and denial of service.

## Patches

Fixed in **1.0.1**. `handlePathPart` now throws a new `ForbiddenKeyError` (also exported) when any path segment is `__proto__`, `constructor`, or `prototype`, regardless of whether the segment would be used as an object key or an array index. The check runs before object/array type branching for defense in depth.

Upgrade:

```
npm install parse-nested-form-data@^1.0.1
```

## Workarounds

If upgrading is not possible, validate field names before calling `parseFormData()`:

```js
const FORBIDDEN = /(^|\.)(__proto__|constructor|prototype)($|[.[])/;
for (const [name] of formData.entries()) {
  if (FORBIDDEN.test(name)) throw new Error('Unsafe field name');
}
```

## Resources

- CWE-1321: Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution')
- Fix commit: 527ad58eb486e32438f7198fb88315c20449d792

## References
- https://github.com/milamer/parse-nested-form-data/security/advisories/GHSA-xp7r-j8r6-j9h3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45302
- https://github.com/milamer/parse-nested-form-data/commit/527ad58eb486e32438f7198fb88315c20449d792
- https://github.com/milamer/parse-nested-form-data
- https://github.com/milamer/parse-nested-form-data/releases/tag/v1.0.1
