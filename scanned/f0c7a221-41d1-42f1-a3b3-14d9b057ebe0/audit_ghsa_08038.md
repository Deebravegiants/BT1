# [H] fast-xml-parser affected by DoS through entity expansion in DOCTYPE (no expansion limit)

## Summary
Severity: High
Advisory: GHSA-jmr7-xgp7-cmfj
CVE: CVE-2026-26278
CWE: CWE-776
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-jmr7-xgp7-cmfj
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=4.1.3 <4.5.4
- npm: `fast-xml-parser` — affected >=5.0.0 <5.3.6

## Details
### Summary
The XML parser can be forced to do an unlimited amount of entity expansion. With a very small XML input, it’s possible to make the parser spend seconds or even minutes processing a single request, effectively freezing the application.

### Details
There is a check in `DocTypeReader.js` that tries to prevent entity expansion attacks by rejecting entities that reference other entities (it looks for & inside entity values). This does stop classic “Billion Laughs” payloads.

However, it doesn’t stop a much simpler variant.

If you define one large entity that contains only raw text (no & characters) and then reference it many times, the parser will happily expand it every time. There is no limit on how large the expanded result can become, or how many replacements are allowed.

The problem is in `replaceEntitiesValue()` inside `OrderedObjParser.js`. It repeatedly runs `val.replace()` in a loop, without any checks on total output size or execution cost. As the entity grows or the number of references increases, parsing time explodes.

Relevant code:

`DocTypeReader.js` (lines 28–33): entity registration only checks for &

`OrderedObjParser.js` (lines 439–458): entity replacement loop with no limits

### PoC

```js
const { XMLParser } = require('fast-xml-parser');

const entity = 'A'.repeat(1000);
const refs = '&big;'.repeat(100);
const xml = `<!DOCTYPE foo [<!ENTITY big "${entity}">]><root>${refs}</root>`;

console.time('parse');
new XMLParser().parse(xml); // ~4–8 seconds for ~1.3 KB of XML
console.timeEnd('parse');

// 5,000 chars × 100 refs takes 200+ seconds
// 50,000 chars × 1,000 refs will hang indefinitely
```

### Impact
This is a straightforward denial-of-service issue.

Any service that parses user-supplied XML using the default configuration is vulnerable. Since Node.js runs on a single thread, the moment the parser starts expanding entities, the event loop is blocked. While this is happening, the server can’t handle any other requests.

In testing, a payload of only a few kilobytes was enough to make a simple HTTP server completely unresponsive for several minutes, with all other requests timing out.

### Workaround

Avoid using DOCTYPE parsing by `processEntities: false` option.

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-jmr7-xgp7-cmfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-26278
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/910dae5be2de2955e968558fadf6e8f74f117a77
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/NaturalIntelligence/fast-xml-parser/releases/tag/v5.3.6
