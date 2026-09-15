# [C] shvl vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-pqwc-3vhw-qcvq
CVE: CVE-2020-28278
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pqwc-3vhw-qcvq
Type: github-advisory

## Affected
- npm: `shvl` — affected >=1.0.0 <2.0.2

## Details
### Overview
Prototype pollution vulnerability in 'shvl' versions 1.0.0 through 2.0.1 allows an attacker to cause a denial of service and may lead to remote code execution.

### Details
The NPM module 'shvl' can be abused by Prototype Pollution vulnerability since the function 'set()' did not check for the type of object before assigning value to the property. Due to this flaw an attacker could create a non-existent property or able to manipulate the property which leads to Denial of Service or potentially Remote code execution.

### PoC Details
The 'set()' function accepts four arguments `object, path, val, obj`. Due to the absence of validation, at values passed into `path, val` arguments, an attacker can supply a malicious value by adjusting the `path` value to include the `__proto__` property. Since there is no validation before assigning property to check whether the assigned `path` is the Object's own property or not, the property `isAdmin` will be directly be assigned to the empty obj({}) thereby polluting the Object prototype. Later in the code, if there is a check to validate `isAdmin` the valued would be substituted as "true" as it had been polluted.

```js
const shvl = require('shvl');
var obj = {}
console.log("Before : " + obj.isAdmin);
shvl.set(obj, '__proto__.isAdmin', true);
console.log("After : " + obj.isAdmin);
```

### Affected Environments
1.0.0-2.0.1

### Remediation
There are a couple of ways to mitigate prototype pollution vulnerabilities, for example: Most of the cases can be solved by freezing an object which doesn’t allow to add, remove, or change its properties. Validating the JSON input with schema validation, this guarantees that the JSON input contains only predefined attributes. We can change the objects, so they won’t have any prototype association by using “Object.create”.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28278
- https://github.com/robinvdvleuten/shvl/issues/34
- https://github.com/robinvdvleuten/shvl/pull/36
- https://github.com/robinvdvleuten/shvl/commit/513c0848774dfb114ad0d0554abf7927cfdd569e
- https://web.archive.org/web/20210320222933/https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28278
