# [C] Command Execution in windows-cpu

## Summary
Severity: Critical
Advisory: GHSA-63m4-fhf2-cmf7
CVE: CVE-2017-1000219
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-63m4-fhf2-cmf7
Type: github-advisory

## Affected
- npm: `windows-cpu` — affected >=0 <0.1.5

## Details
Version of `windows-cpu` before 0.1.5 will execute arbitrary code passed into the first argument of the `findLoad` method, resulting in remote code execution.

## Proof of Concept

```js
var win = require('windows-cpu');
wind.findLoad('foo & calc.exe');
```


## Recommendation

Update to version 0.1.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000219
- https://github.com/KyleRoss/windows-cpu/commit/b75e19aa2f7459a9506bceb577ba2341fe273117
- https://github.com/KyleRoss/windows-cpu
- https://github.com/KyleRoss/windows-cpu/blob/master/index.js#L81
- https://www.npmjs.com/advisories/336
