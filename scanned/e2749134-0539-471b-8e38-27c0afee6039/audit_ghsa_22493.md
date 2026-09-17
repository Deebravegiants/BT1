# [C] flattenizer vulnerable to prototype pollution

## Summary
Severity: Critical
Advisory: GHSA-vq33-26pr-r4h6
CVE: CVE-2020-28279
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vq33-26pr-r4h6
Type: github-advisory

## Affected
- npm: `flattenizer` — affected >=0.0.5 <1.1.1

## Details
### Overview
Prototype pollution vulnerability in ‘flattenizer’ versions 0.0.5 through 1.0.5 allows an attacker to cause a denial of service and may lead to remote code execution.

### Details
The NPM module 'flattenizer' can be abused by Prototype Pollution vulnerability since the function 'unflatten()' did not check for the type of object before assigning value to the property. Due to this flaw an attacker could create a non-existent property or able to manipulate the property which leads to Denial of Service or potentially Remote code execution.

### PoC Details
There is no validation before assigning the property to check whether the assigned argument is the Object's own property or not, the property `polluted` will be directly be assigned thereby polluting the Object prototype. Later in the code, if there is a check to validate `polluted` the valued would be substituted as "true" as it had been polluted.

```js
var flattenizer = require("flattenizer")
flattenizer.unflatten({'__proto__.polluted': true});
console.log(polluted);
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28279
- https://github.com/sahellebusch/flattenizer/pull/13
- https://github.com/sahellebusch/flattenizer/commit/3c6a6353df7c8879e931973b81a49a47f6c2b399
- https://web.archive.org/web/20210104205035/https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28279
