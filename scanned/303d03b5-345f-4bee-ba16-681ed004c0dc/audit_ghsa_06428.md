# [M] Tiptap: mergeAttributes() turns an own __proto__ key into inherited executable DOM attributes

## Summary
Severity: Medium
Advisory: GHSA-cp6q-959q-f8rh
CWE: CWE-1321, CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-cp6q-959q-f8rh
Type: github-advisory

## Affected
- npm: `@tiptap/core` — affected >=2.0.0-alpha.0 <3.30.4

## Details
## Summary

`@tiptap/core`'s public `mergeAttributes()` helper uses ordinary bracket assignment on keys returned by `Object.entries()`. An own `__proto__` key from JSON therefore invokes the legacy prototype setter on the fresh merged object. The function returns an object whose prototype is attacker-controlled, while `Object.keys()` and ordinary own-property checks show no attacker attributes.

When that result is used as a ProseMirror DOMOutputSpec attribute object, `prosemirror-model`'s `DOMSerializer.renderSpec()` enumerates it with `for...in` and applies inherited values with `setAttribute()`. In a browser proof, inherited `src` and `onerror` values were copied to an `<img>` and the error handler executed once. This is per-object prototype manipulation; the proof does not modify global `Object.prototype`.

## Root cause

The affected loop is conceptually:

```ts
const mergedAttributes = { ...items }
for (const [key, value] of Object.entries(item)) {
  const exists = mergedAttributes[key]
  // ...
  mergedAttributes[key] = value
}
```

`Object.entries(JSON.parse('{"__proto__": {...}}'))` includes `__proto__`. Reading `mergedAttributes['__proto__']` resolves the inherited `Object.prototype`; assigning to the same key invokes `Object.prototype.__proto__`'s setter and replaces `mergedAttributes`' prototype.

## Browser reproduction

The following shape was tested with exact `@tiptap/core` 3.29.2 and `prosemirror-model` 1.25.11:

```js
const input = JSON.parse(`{
  "__proto__": {
    "data-inherited-canary": "present",
    "src": "x-invalid://canary",
    "onerror": "globalThis.__tiptapXss += 1"
  }
}`)

const attrs = mergeAttributes(input)
// Object.keys(attrs) === []
// Object.getPrototypeOf(attrs) === input.__proto__

const schema = new Schema({
  nodes: {
    doc: { content: 'image' },
    image: { toDOM: () => ['img', attrs] },
    text: {},
  },
})
const doc = schema.node('doc', null, [schema.node('image')])
const fragment = DOMSerializer.fromSchema(schema).serializeFragment(doc.content)
document.body.append(fragment)
```

Chromium produced an image with `data-inherited-canary`, `src`, and `onerror`; the handler executed exactly once. `Object.prototype` remained clean.

## Impact and preconditions

Applications that merge untrusted imported document, plugin, CMS, API, tenant, or AI-derived attribute objects can receive a prototype-manipulated result. Consumers that enumerate inherited keys, including ProseMirror's DOM serializer, can turn the hidden properties into DOM attributes and execute JavaScript in the application's origin. Own-key validation, object spread, JSON serialization, and logging can miss the inherited values. Other component consumers can read inherited authorization or configuration fields.

Tiptap's standard fixed ProseMirror schemas discard unknown document attributes, so arbitrary Tiptap JSON is not automatically exploitable in every application. A vulnerable application needs an untrusted object boundary into `mergeAttributes()` or a dynamic/custom extension or schema that preserves the relevant attribute object.

## Affected versions

The unsafe assignment was introduced in commit `ecadf7ea0a7f8f39a8496a60edf0ac8f379e6eb3` and is present in the first package tag `@tiptap/core@2.0.0-alpha.0`, v2.0.0, v2.27.1, v3.0.0, and current v3.29.2 source. No fixed release was found.

## Recommended remediation

Reject `__proto__` before reading or assigning the key, or define copied keys as own data properties without invoking legacy setters. A minimal hardening is to skip `key === '__proto__'`. Add regression tests using an own JSON-origin `__proto__` key and assert that the result keeps `Object.prototype` as its prototype, exposes no inherited attacker keys, and cannot create an event-handler attribute through `DOMSerializer`.

This was found during authorized dependency review and is being reported privately. No public zero-day issue has been opened.

## References
- https://github.com/ueberdosis/tiptap/security/advisories/GHSA-cp6q-959q-f8rh
- https://github.com/ueberdosis/tiptap/commit/01d7af8c983ee5954c63734f4fa46cb23ae3246d
- https://github.com/ueberdosis/tiptap
- https://github.com/ueberdosis/tiptap/releases/tag/v3.30.4
