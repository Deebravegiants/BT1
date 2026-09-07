# [H] xmldom has XML node injection through unvalidated comment serialization

## Summary
Severity: High
Advisory: GHSA-j759-j44w-7fr8
CVE: CVE-2026-41672
CWE: CWE-91
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-j759-j44w-7fr8
Type: github-advisory

## Affected
- npm: `@xmldom/xmldom` — affected >=0 <0.8.13
- npm: `@xmldom/xmldom` — affected >=0.9.0 <0.9.10
- npm: `xmldom` — affected >=0

## Details
## Summary

The package allows attacker-controlled comment content to be serialized into XML without validating or neutralizing comment breaking sequences. As a result, an attacker can terminate the comment early and inject arbitrary XML nodes into the serialized output.

---

## Details

The issue is in the DOM construction and serialization flow for comment nodes.

When `createComment(data)` is called, the supplied string is stored as comment data through the generic character-data handling path. That content is kept as-is. Later, when the document is serialized, the serializer writes comment nodes by concatenating the XML comment delimiters with the stored `node.data` value directly.

That behavior is unsafe because XML comments are a syntax-sensitive context. If attacker-controlled input contains a sequence that closes the comment, the serializer does not preserve it as literal comment text. Instead, it emits output where the remainder of the payload is treated as live XML markup.

This is a real injection bug, not a formatting issue. The serializer already applies context-aware handling in other places, such as escaping text nodes and rewriting unsafe CDATA terminators. Comment content does not receive equivalent treatment. Because of that gap, untrusted data can break out of the comment boundary and modify the structure of the final XML document.

---

## PoC

```js
const { DOMImplementation, DOMParser, XMLSerializer } = require('@xmldom/xmldom');

const doc = new DOMImplementation().createDocument(null, 'root', null);

doc.documentElement.appendChild(
  doc.createComment('--><injected attr="1"/><!--')
);

const xml = new XMLSerializer().serializeToString(doc);
console.log(xml);
// <root><!----><injected attr="1"/><!----></root>

const reparsed = new DOMParser().parseFromString(xml, 'text/xml');
console.log(reparsed.documentElement.childNodes.item(1).nodeName);
// injected
```

---

## Impact

An application that uses the package to build XML from untrusted input can be made to emit attacker-controlled elements outside the intended comment boundary. That allows the attacker to alter the meaning and structure of generated XML documents.

In practice, this can affect any workflow that generates XML and then stores it, forwards it, signs it, or hands it to another parser. Realistic targets include XML-based configuration, policy documents, and message formats where downstream consumers trust the serialized structure.

---

## Disclosure

This vulnerability was publicly disclosed at 2026-04-06T11:25:07Z via [xmldom/xmldom#987](https://github.com/xmldom/xmldom/pull/987), which was subsequently closed without being merged.

---

## Fix Applied

> **⚠ Opt-in required.** Protection is not automatic. Existing serialization calls remain
> vulnerable unless `{ requireWellFormed: true }` is explicitly passed. Applications that pass
> untrusted data to `createComment()` or mutate comment nodes with untrusted input (via
> `appendData`, `insertData`, `replaceData`, `.data =`, or `.textContent =`) should audit all
> `serializeToString()` call sites and add the option.

`XMLSerializer.serializeToString()` now accepts an options object as a second argument. When `{ requireWellFormed: true }` is passed, the serializer throws `InvalidStateError` before emitting a Comment node whose `.data` would produce malformed XML.

On `@xmldom/xmldom` ≥ 0.9.10, the full W3C DOM Parsing §3.2.1.4 check is applied: throws if `.data` contains `--` anywhere, ends with `-`, or contains characters outside the XML Char production.

On `@xmldom/xmldom` ≥ 0.8.13 (LTS), only the `-->` injection sequence is checked. The `0.8.x` SAX parser accepts comments containing `--` (without `>`), so throwing on bare `--` would break a previously-working round-trip on that branch. The `-->` check is sufficient to prevent injection.

### PoC — fixed path

```js
const { DOMImplementation, XMLSerializer } = require('@xmldom/xmldom');

const doc = new DOMImplementation().createDocument(null, 'root', null);
doc.documentElement.appendChild(doc.createComment('--><injected attr="1"/><!--'));

// Default (unchanged): verbatim — injection present
const unsafe = new XMLSerializer().serializeToString(doc);
console.log(unsafe);
// <root><!----><injected attr="1"/><!----></root>

// Opt-in guard: throws InvalidStateError before serializing
try {
  new XMLSerializer().serializeToString(doc, { requireWellFormed: true });
} catch (e) {
  console.log(e.name, e.message);
  // InvalidStateError: The comment node data contains "--" or ends with "-"  (0.9.x)
  // InvalidStateError: The comment node data contains "-->"  (0.8.x — only --> is checked)
}
```

### Why the default stays verbatim

The W3C DOM Parsing and Serialization spec §3.2.1.4 defines a `require well-formed` flag whose **default value is `false`**. With the flag unset, the spec explicitly permits serializing ill-formed comment content verbatim — this is also the behavior of browser implementations (Chrome, Firefox, Safari): `new XMLSerializer().serializeToString(doc)` produces the injection sequence without error in all major browsers.

Unconditionally throwing would be a behavioral breaking change with no spec justification. The opt-in `requireWellFormed: true` flag allows applications that require injection safety to enable strict mode without breaking existing deployments.

### Residual limitation

The fix operates at serialization time only. There is no creation-time check in `createComment` — the spec does not require one for comment data. Any path that leads to a Comment node with `--` in its data (`createComment`, `appendData`, `.data =`, etc.) produces a node that serializes safely only when `{ requireWellFormed: true }` is passed to `serializeToString`.

## References
- https://github.com/xmldom/xmldom/security/advisories/GHSA-j759-j44w-7fr8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41672
- https://github.com/xmldom/xmldom/pull/987
- https://github.com/xmldom/xmldom/commit/b397540889086da868c30c366ad5c220d1a750c7
- https://github.com/xmldom/xmldom/commit/fda7cc313de30243fea35cada64e0bb12099c2a1
- https://github.com/xmldom/xmldom
- https://github.com/xmldom/xmldom/releases/tag/0.8.13
- https://github.com/xmldom/xmldom/releases/tag/0.9.10
