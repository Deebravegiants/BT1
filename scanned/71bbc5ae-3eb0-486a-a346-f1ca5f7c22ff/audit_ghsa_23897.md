# [C] dset vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-q4xc-7cw8-cgfj
CVE: CVE-2020-28277
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q4xc-7cw8-cgfj
Type: github-advisory

## Affected
- npm: `dset` — affected >=1.0.0 <2.0.1

## Details
### Overview
Prototype pollution vulnerability in 'dset' versions 1.0.0 through 2.0.1 allows attacker to cause a denial of service and may lead to remote code execution.

### Details
The NPM module 'dset' can be abused by Prototype Pollution vulnerability since the function ‘export ()' did not check for the type of object before assigning value to the property. Due to this flaw an attacker could create a non-existent property or able to manipulate the property which leads to Denial of Service or potentially Remote code execution.

### PoC
The export function accepts three arguments `obj, keys, val`. Due to the absence of validation, at values passed into `keys, val` arguments, an attacker can supply a malicious value by adjusting the `keys` value to include the `__proto__` property. Since there is no validation before assigning property to check whether the assigned `keys` is the Object's own property or not, the property `isAdmin` will be directly be assigned to the empty obj({}) thereby polluting the Object prototype. Later in the code, if there is a check to validate `isAdmin` the valued would be substituted as "true" as it had been polluted.

```js
const dset = require('dset');
var obj = {}
console.log("Before : " + obj.isAdmin);
dset(obj, '__proto__.polluted', true);
console.log("After : " + obj.polluted);
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28277
- https://github.com/lukeed/dset/issues/11
- https://github.com/lukeed/dset/commit/2b9ec49e231107b1a83b04a1bc1a66a8d14cea1c
- https://github.com/lukeed/dset/blob/50a6ead172d1466a96035eff00f8eb465ccd050a/src/index.js#L6
- https://web.archive.org/web/20210104204657/https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28277
