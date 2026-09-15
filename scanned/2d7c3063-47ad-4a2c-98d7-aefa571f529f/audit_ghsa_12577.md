# [M] fast-xml-parser vulnerable to Prototype Pollution through tag or attribute name

## Summary
Severity: Medium
Advisory: GHSA-x3cc-x39p-42qx
CVE: CVE-2023-26920
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-06-13
Source: https://github.com/advisories/GHSA-x3cc-x39p-42qx
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=0 <4.1.2

## Details
### Impact
As a part of this vulnerability, user was able to se code using `__proto__` as a tag or attribute name.

```js
const { XMLParser, XMLBuilder, XMLValidator} = require("fast-xml-parser");

let XMLdata = "<__proto__><polluted>hacked</polluted></__proto__>"

const parser = new XMLParser();
let jObj = parser.parse(XMLdata);

console.log(jObj.polluted) // should return hacked
``` 

### Patches
The problem has been patched in v4.1.2

### Workarounds
User can check for "__proto__" in the XML string before parsing it to the parser.

### References
https://gist.github.com/Sudistark/a5a45bd0804d522a1392cb5023aa7ef7

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-x3cc-x39p-42qx
- https://nvd.nist.gov/vuln/detail/CVE-2023-26920
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/2b032a4f799c63d83991e4f992f1c68e4dd05804
- https://gist.github.com/Sudistark/a5a45bd0804d522a1392cb5023aa7ef7
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/advisories/GHSA-793h-6f7r-6qvm
