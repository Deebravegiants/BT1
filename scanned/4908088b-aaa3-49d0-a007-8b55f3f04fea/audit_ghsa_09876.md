# [H] xmldom: XML injection via unsafe CDATA serialization allows attacker-controlled markup insertion

## Summary
Severity: High
Advisory: GHSA-wh4c-j3r5-mjhp
CVE: CVE-2026-34601
CWE: CWE-91
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-wh4c-j3r5-mjhp
Type: github-advisory

## Affected
- npm: `xmldom` — affected >=0
- npm: `@xmldom/xmldom` — affected >=0 <0.8.12
- npm: `@xmldom/xmldom` — affected >=0.9.0 <0.9.9

## Details
## Summary

`@xmldom/xmldom` allows attacker-controlled strings containing the CDATA terminator `]]>` to be inserted into a `CDATASection` node. During serialization, `XMLSerializer` emitted the CDATA content verbatim without rejecting or safely splitting the terminator. As a result, data intended to remain text-only became **active XML markup** in the serialized output, enabling XML structure
injection and downstream business-logic manipulation.

The sequence `]]>` is not allowed inside CDATA content and must be rejected or safely handled during serialization. ([MDN Web Docs](https://developer.mozilla.org/))

### Attack surface

`Document.createCDATASection(data)` is the most direct entry point, but it is not the only one. The WHATWG DOM spec intentionally does not validate `]]>` in mutation methods — only `createCDATASection` carries that guard. The following paths therefore also allow `]]>` to enter a CDATASection node and reach the serializer:

- `CharacterData.appendData()`
- `CharacterData.replaceData()`
- `CharacterData.insertData()`
- Direct assignment to `.data`
- Direct assignment to `.textContent`

(Note: assigning to `.nodeValue` does **not** update `.data` in this implementation — the serializer reads `.data` directly — so `.nodeValue` is not an exploitable path.)

### Parse path

Parsing XML that contains a CDATA section is **not** affected. The SAX parser's non-greedy `CDSect` regex stops at the first `]]>`, so parsed CDATA data never contains the terminator.

---

## Impact

If an application uses `xmldom` to generate "trusted" XML documents that embed **untrusted user input** inside CDATA (a common pattern in exports, feeds, SOAP/XML integrations, etc.), an attacker can inject additional XML elements/attributes into the generated document.

This can lead to:

- Integrity violation of generated XML documents.
- Business-logic injection in downstream consumers (e.g., injecting `<approved>true</approved>`,  `<role>admin</role>`, workflow flags, or other security-relevant elements).
- Unexpected privilege/workflow decisions if downstream logic assumes injected nodes cannot appear.

This issue does **not** require malformed parsers or browser behavior; it is caused by serialization producing attacker-influenced XML markup.

---

## Root Cause (with file + line numbers)

**File:** `lib/dom.js`

### 1. No validation in `createCDATASection`

`createCDATASection: function (data)` accepts any string and appends it directly.

- **Lines 2216–2221** (0.9.8)

### 2. Unsafe CDATA serialization

Serializer prints CDATA sections as:

```
<![CDATA[ + node.data + ]]>
```

without handling `]]>` in the data.

- **Lines 2919–2920** (0.9.8)

Because CDATA content is emitted verbatim, an embedded `]]>` closes the CDATA section early and the remainder of the attacker-controlled payload is interpreted as markup in the serialized XML.

---

## Proof of Concept — Fix A: `createCDATASection` now throws

On patched versions, passing `]]>` directly to `createCDATASection` throws `InvalidCharacterError` instead of silently accepting the payload:

```js
const { DOMImplementation } = require('./lib');

const doc = new DOMImplementation().createDocument(null, 'root', null);
try {
  doc.createCDATASection('SAFE]]><injected attr="pwn"/>');
  console.log('VULNERABLE — no error thrown');
} catch (e) {
  console.log('FIXED — threw:', e.name); // InvalidCharacterError
}
```

Expected output on patched versions:

```
FIXED — threw: InvalidCharacterError
```

---

## Proof of Concept — Fix B: mutation vector now safe

On patched versions, injecting `]]>` via a mutation method (`appendData`, `replaceData`, `.data =`, `.textContent =`) no longer produces injectable output. The serializer splits the terminator so the result round-trips as safe text:

```js
const { DOMImplementation, XMLSerializer } = require('./lib');
const { DOMParser } = require('./lib');

const doc = new DOMImplementation().createDocument(null, 'root', null);

// Start with safe data, then mutate to include the terminator
const cdata = doc.createCDATASection('safe');
doc.documentElement.appendChild(cdata);
cdata.appendData(']]><injected attr="pwn"/><more>TEXT</more><![CDATA[');

const out = new XMLSerializer().serializeToString(doc);
console.log('Serialized:', out);

const reparsed = new DOMParser().parseFromString(out, 'text/xml');
const injected = reparsed.getElementsByTagName('injected').length > 0;
console.log('Injected element found in reparsed doc:', injected);
// VULNERABLE: true  |  FIXED: false
```

Expected output on patched versions:

```
Serialized: <root><![CDATA[safe]]]]><![CDATA[><injected attr="pwn"/><more>TEXT</more><![CDATA[]]></root>
Injected element found in reparsed doc: false
```

---

## Fix Applied

Both mitigations were implemented:

### Option A — Strict/spec-aligned: reject `]]>` in `createCDATASection()`

`Document.createCDATASection(data)` now throws `InvalidCharacterError` (per the [WHATWG DOM spec](https://dom.spec.whatwg.org/#dom-document-createcdatasection)) when `data` contains `]]>`. This closes the direct entry point.

Code that previously passed a string containing `]]>` to `createCDATASection` and relied on the silent/unsafe behaviour will now receive `InvalidCharacterError`. Use a mutation method such as `appendData` if you intentionally need `]]>` in a CDATASection node's data (the serializer split in Option B will keep the output safe).

### Option B — Defensive serialization: split the terminator during serialization

`XMLSerializer` now replaces every occurrence of `]]>` in CDATA section data with the split sequence `]]]]><![CDATA[>` before emitting. This closes all mutation-vector paths that Option A alone cannot guard, and means the serialized output is always well-formed XML regardless of how `]]>` entered the node.

## Update — 2026-04-xx (0.9.10 / 0.8.13)

### `splitCDATASections` is deprecated

The CDATA split behavior introduced as Option B of this fix (replacing `]]>` with`]]]]><![CDATA[>` during serialization) is **deprecated** as of 0.9.10 / 0.8.13.

This release introduces a `requireWellFormed` option on `XMLSerializer.serializeToString()`. When `{ requireWellFormed: true }` is passed as the second argument, the serializer throws `InvalidStateError` if CDATA section data contains `]]>` — this is the spec-aligned behavior (W3C DOM Parsing and Serialization, `require well-formed` flag) and the recommended migration path going forward.
The split behavior is now controlled by an explicit `splitCDATASections` option (default `true`, preserving the current behavior). The three serialization behaviors are:
| `requireWellFormed` | `splitCDATASections` | Behavior ||---|---|---|| `false` (default) | `true` (default) | Split `]]>` → `]]]]><![CDATA[>` (current behavior, deprecated) || `true` | — (ignored) | Throw `InvalidStateError` — spec-aligned, recommended |\ `false` | `false` | Emit verbatim — same as pre-0.9.9 behavior |

`requireWellFormed: true` takes precedence: the split path is unreachable when it is set.

### Migration
Replace any reliance on the default split behavior with an explicit opt-in:
```js// Before (implicit split, deprecated): const xml = new XMLSerializer().serializeToString(doc);

// After (explicit guard, spec-aligned): const xml = new XMLSerializer().serializeToString(doc, { requireWellFormed: true }); // Throws InvalidStateError if any CDATASection contains ']]>' ```

### Removal timeline
Both the `splitCDATASections` option and the underlying `]]>` → `]]]]><![CDATA[>` split mechanics will be removed in the next breaking (`0.10.0`) release. After removal, the only behaviors will be verbatim (default) and `requireWellFormed: true` (throws).

Removal is tracked in [xmldom/xmldom#999](https://github.com/xmldom/xmldom/issues/999).

## References
- https://github.com/xmldom/xmldom/security/advisories/GHSA-wh4c-j3r5-mjhp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34601
- https://github.com/xmldom/xmldom/commit/2b852e836ab86dbbd6cbaf0537f584dd0b5ac184
- https://github.com/xmldom/xmldom
- https://github.com/xmldom/xmldom/releases/tag/0.8.12
- https://github.com/xmldom/xmldom/releases/tag/0.9.9
