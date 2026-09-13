# [M] next-intl has prototype pollution with `experimental.messages.precompile` via attacker-controlled translation catalog keys

## Summary
Severity: Medium
Advisory: GHSA-4c35-wcg5-mm9h
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-4c35-wcg5-mm9h
Type: github-advisory

## Affected
- npm: `next-intl` — affected >=0 <4.9.2

## Details
## Summary

`setNestedProperty` in `packages/next-intl/src/extractor/utils.tsx` walks a dotted key path and assigns the final value without blocking the reserved keys `__proto__`, `constructor`, or `prototype`. When the next-intl Next.js plugin is configured with `experimental.messages` and `messages.precompile: true`, a JSON translation catalog containing a top‑level `__proto__` key causes `setNestedProperty(result, '__proto__.isAdmin', compiledMessage)` to assign onto `Object.prototype`, polluting every object in the running build process.

## Details

Root cause — `packages/next-intl/src/extractor/utils.tsx:13-34`:

```ts
export function setNestedProperty(
  obj: Record<string, any>,
  keyPath: string,
  value: any
): void {
  const keys = keyPath.split('.');
  let current = obj;

  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (
      !(key in current) ||
      typeof current[key] !== 'object' ||
      current[key] === null
    ) {
      current[key] = {};
    }
    current = current[key];
  }

  current[keys[keys.length - 1]] = value;
}
```

The existence check `!(key in current)` uses the `in` operator, which walks the prototype chain. For `key === '__proto__'`, `'__proto__' in {}` is `true` (it's inherited from `Object.prototype`) and `typeof current['__proto__'] === 'object'` (it *is* `Object.prototype`). The guard therefore never re-initializes `current[key]`, and `current = current['__proto__']` redirects all subsequent writes onto `Object.prototype`. The final assignment `current[keys[keys.length-1]] = value` sets `Object.prototype[<attacker key>] = <attacker value>`.

Build-time data flow:

1. `packages/next-intl/src/plugin/catalog/catalogLoader.tsx:55-83` — the webpack/turbopack loader receives the catalog file `source` and, if `options.messages.precompile` is enabled, calls `codec.decode(source, {locale})`.
2. `packages/next-intl/src/extractor/format/codecs/JSONCodec.tsx:9-18` — `decode` runs `JSON.parse(source)`. V8 installs `__proto__` as an **own data property** on the result when the JSON key is literally `"__proto__"` (bypassing the normal `Object.prototype.__proto__` setter that would otherwise reassign the prototype).
3. `JSONCodec.tsx:33-53` — `traverseMessages` iterates `Object.keys(obj)`, which for a JSON‑parsed object includes the own `__proto__` key. It reads `obj.__proto__` (returns the attacker’s nested object, not `Object.prototype`, because it's an own property), recurses into it, and emits message id `__proto__.isAdmin`.
4. `catalogLoader.tsx:71` — `precompileMessages(decoded, cache)`.
5. `catalogLoader.tsx:89-131` — for each message, calls `setNestedProperty(result, message.id, compiledMessage)`. With `message.id === '__proto__.isAdmin'`, `setNestedProperty` walks into `Object.prototype` and assigns `Object.prototype.isAdmin = compiledMessage`.

The same sink is also reachable via `JSONCodec.encode` (`JSONCodec.tsx:20-26`) and `POCodec` (`packages/next-intl/src/extractor/format/codecs/POCodec.tsx:87`) during extraction, both of which feed attacker-influenced `message.id` values into `setNestedProperty` — but those paths require control of source-code identifiers, which is a weaker attack vector than the build-time catalog path above.

After pollution, every subsequent object access during the remainder of the Next.js build pipeline (webpack, turbopack, babel, next-intl’s own logic) inherits the attacker-controlled properties. This is a classic gadget-chain precondition for corrupting build-tool internals and tampering with generated bundles, since many build tools use patterns like `if (obj.someFlag)` or `options[key] ?? default` that are sensitive to polluted prototypes.

Trust boundary note: next-intl’s message catalogs are realistically attacker-influenced in practice. Translation files are routinely round-tripped through external TMS systems (Crowdin, Lokalise, Transifex), accepted via community locale PRs, or pulled from third-party translation packages — any of which can carry a crafted `__proto__` key unnoticed, since JSON translation diffs are usually merged with minimal scrutiny.

## PoC

Prerequisites: a Next.js project using next-intl ≤ 4.9.1 with the Next.js plugin configured:

```ts
// next.config.ts
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin({
  experimental: {
    messages: {
      path: './messages',
      format: 'json',
      locales: 'infer',
      precompile: true
    }
  }
});

export default withNextIntl({});
```

1. Drop a malicious catalog at `messages/en.json`:

   ```json
   {
     "Greeting": "Hello",
     "__proto__": { "isAdmin": "polluted" }
   }
   ```

2. Run `next build` (or `next dev`). The `catalogLoader` will invoke `JSONCodec.decode` → `traverseMessages` → `precompileMessages` → `setNestedProperty`.

3. Minimal reproduction of the sink itself (verified locally against the v4.9.1 source):

   ```js
   function setNestedProperty(obj, keyPath, value) {
     const keys = keyPath.split('.');
     let current = obj;
     for (let i = 0; i < keys.length - 1; i++) {
       const key = keys[i];
       if (!(key in current) || typeof current[key] !== 'object' || current[key] === null) {
         current[key] = {};
       }
       current = current[key];
     }
     current[keys[keys.length - 1]] = value;
   }

   setNestedProperty({}, '__proto__.isAdmin', 'PWNED');
   console.log(({}).isAdmin); // -> "PWNED"
   ```

   Output: `PWNED`.

4. Full chain reproduction (also verified):

   ```js
   const parsed = JSON.parse('{"Greeting":"Hello","__proto__":{"isAdmin":"polluted"}}');
   // traverseMessages emits: [{id:"Greeting",message:"Hello"},{id:"__proto__.isAdmin",message:"polluted"}]
   // precompileMessages then calls setNestedProperty(result, "__proto__.isAdmin", "polluted")
   console.log(({}).isAdmin); // -> "polluted"
   ```

   After the loader runs, `({}).isAdmin === 'polluted'` for the remainder of the build Node process.

## Impact

- `Object.prototype` is polluted for the lifetime of the build‑time Node.js process, affecting every object created or inspected thereafter in the Next.js build pipeline (webpack/turbopack loaders, babel plugins, next-intl’s own codecs, user plugins).
- Classic CWE-1321 gadget-chain precondition: downstream tools that branch on `obj.someFlag`, `options[key] ?? default`, `if (!config.noX)`, etc. can be coerced into unintended behavior, including emitting tampered bundles.
- Realistic delivery vectors include TMS round-trips (Crowdin/Lokalise/Transifex), community locale PRs, and compromised/transitively-installed translation packages — all situations where a JSON catalog diff is routinely accepted without the scrutiny given to code changes.
- Exploitation requires the user to opt in to the `experimental.messages` + `precompile` configuration. Users who do not use the extractor/precompile features are not affected.

## Recommended Fix

Reject reserved keys in `setNestedProperty` and stop using the `in` operator for the existence check. A minimal patch to `packages/next-intl/src/extractor/utils.tsx`:

```ts
const FORBIDDEN_KEYS = new Set(['__proto__', 'constructor', 'prototype']);

export function setNestedProperty(
  obj: Record<string, any>,
  keyPath: string,
  value: any
): void {
  const keys = keyPath.split('.');
  for (const key of keys) {
    if (FORBIDDEN_KEYS.has(key)) {
      throw new Error(`Invalid message id segment: ${key}`);
    }
  }

  let current = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (
      !Object.prototype.hasOwnProperty.call(current, key) ||
      typeof current[key] !== 'object' ||
      current[key] === null
    ) {
      current[key] = Object.create(null);
    }
    current = current[key];
  }

  current[keys[keys.length - 1]] = value;
}
```

Additionally:

- In `packages/next-intl/src/extractor/format/codecs/JSONCodec.tsx`, make `traverseMessages` skip reserved keys (or switch to `Object.create(null)` + `Object.hasOwn` semantics) so that a malicious catalog is rejected early with a clear error rather than producing `__proto__.*` message ids.
- In `packages/next-intl/src/plugin/catalog/catalogLoader.tsx`, initialize `precompileMessages`’s `result` with `Object.create(null)` as defense in depth, so even if a key slipped through it could not redirect through `Object.prototype`.

## References
- https://github.com/amannn/next-intl/security/advisories/GHSA-4c35-wcg5-mm9h
- https://github.com/amannn/next-intl
