# [C] keyget vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-8mp8-28xh-r486
CVE: CVE-2020-28272
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8mp8-28xh-r486
Type: github-advisory

## Affected
- npm: `keyget` — affected >=1.0.0 <2.3.0

## Details
### Overview
Prototype pollution vulnerability in 'keyget' versions 1.0.0 through 2.2.0 allows attacker to cause a denial of service and may lead to remote code execution.

### Details
The npm module 'keyget' can be abused by Prototype Pollution vulnerability since the function 'setByPath()' did not check for the type of object before assigning value to the property. Due to this flaw an attacker could create a non-existent property or able to manipulate the property which leads to Denial of Service or potentially Remote code execution.

### PoC Details
The `setByPath()` function accepts three arguments `target, path, value`. Due to the absence of validation, at values passed into `path, value` an attacker can supply a malicious value by adjusting the `path` value to include the `__proto__` property. Since there is no validation before assigning property to check whether the assigned `path` is the Object's own property or not, the property `polluted` will be directly be assigned to the empty obj({}) thereby polluting the Object prototype. Later in the code, if there is a check to validate `polluted` the value would be substituted as "true" as it had been polluted.

### PoC Code
```js
var keyget = require("keyget")
 keyget.set({}, '__proto__.polluted', 'true');
 console.log(polluted); 
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28272
- https://github.com/rumkin/keyget/commit/17d15b6c75036eb429075a8cfeccfc18094dd2e2
- https://github.com/rumkin/keyget
- https://web.archive.org/web/20201207183211/https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28272
