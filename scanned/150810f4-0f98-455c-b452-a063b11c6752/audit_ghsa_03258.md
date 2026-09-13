# [C] Code injection in mock2easy

## Summary
Severity: Critical
Advisory: GHSA-g4xj-wcq6-qwx5
CVE: CVE-2020-7697
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-g4xj-wcq6-qwx5
Type: github-advisory

## Affected
- npm: `mock2easy` — affected >=0

## Details
This affects all versions up to and including version 0.0.24 of package mock2easy. a malicious user could inject commands through the `_data` variable: 

Affected Area

```js
require('../server/getJsonByCurl')(mock2easy, function(error, stdout) {
    if (error) {
        return res.json(500, error);
    }
    res.json(JSON.parse(stdout));
}, '', _data.interfaceUrl, query, _data.cookie, _data.interfaceType);```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7697
- https://github.com/appLhui/mock2easy/blob/1da728fa0f61cc29fb415f0677e54ad4902261d3/routes/index.js#L132-L139
- https://snyk.io/vuln/SNYK-JS-MOCK2EASY-572312
- https://www.npmjs.com/package/mock2easy
