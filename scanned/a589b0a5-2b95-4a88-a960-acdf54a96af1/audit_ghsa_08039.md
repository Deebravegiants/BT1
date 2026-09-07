# [M] dottie is vulnerable to Prototype Pollution bypass via non-first path segments in set() and transform()

## Summary
Severity: Medium
Advisory: GHSA-r5mx-6wc6-7h9w
CVE: CVE-2026-27837
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-r5mx-6wc6-7h9w
Type: github-advisory

## Affected
- npm: `dottie` — affected >=2.0.4 <2.0.7

## Details
### Summary

dottie versions 2.0.4 through 2.0.6 contain an incomplete fix for CVE-2023-26132. The prototype pollution guard introduced in commit `7d3aee1` only validates the first segment of a dot-separated path, allowing an attacker to bypass the protection by placing `__proto__` at any position other than the first.

Both `dottie.set()` and `dottie.transform()` are affected.

### Details

The existing guard checks only `pieces[0] === '__proto__'`. When a path like `'a.__proto__.polluted'` is used, `pieces[0]` evaluates to `'a'`, not `'__proto__'`, so the guard is bypassed.

Inside the traversal loop, `current['__proto__'] = {}` triggers the `__proto__` setter, replacing the intermediate object's prototype. The final value is then written onto this new prototype.

**Important distinction:** This vulnerability does NOT pollute the global `Object.prototype`. It injects properties into a specific object's prototype chain. However, injected properties are invisible to `hasOwnProperty()` and `Object.keys()`, which makes them difficult to detect and can lead to authorization bypass in common coding patterns.

### PoC
```javascript
const dottie = require('dottie');

// set() bypass
const obj = {};
dottie.set(obj, 'session.__proto__.isAdmin', true);
console.log(obj.session.isAdmin);                    // true
console.log(({}).isAdmin);                           // undefined
console.log(obj.session.hasOwnProperty('isAdmin'));  // false

// transform() bypass
const flat = { 'user.__proto__.role': 'admin', 'user.name': 'guest' };
const result = dottie.transform(flat);
console.log(result.user.role);                       // 'admin'
console.log(({}).role);                              // undefined
```

Tested on Node.js v20 and v22, dottie 2.0.6, Windows 11.

### Impact

The primary risk is authorization bypass. In a typical server-side scenario where dottie is used to process user input (e.g., via Sequelize, which depends on dottie with ~1.3M weekly npm downloads), an attacker can inject properties like `isAdmin: true` into objects used for access control decisions. Since the injected property is not an own property, standard checks using `hasOwnProperty()` or `Object.keys()` will not reveal it, while property access like `if (session.isAdmin)` will return `true`.

Additionally, replacing an object's prototype via `current['__proto__'] = {}` strips all inherited methods, potentially causing TypeError exceptions and denial of service.

## References
- https://github.com/mickhansen/dottie.js/security/advisories/GHSA-r5mx-6wc6-7h9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-27837
- https://github.com/mickhansen/dottie.js/commit/7e8fa1345a4b46325f0eab8d7aeb1c4deaefdb14
- https://github.com/advisories/GHSA-4gxf-g5gf-22h4
- https://github.com/mickhansen/dottie.js
