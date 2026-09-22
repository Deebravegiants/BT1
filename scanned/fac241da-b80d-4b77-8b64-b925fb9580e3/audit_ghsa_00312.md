# [C] Sandbox Breakout in safe-eval

## Summary
Severity: Critical
Advisory: GHSA-ww6v-677g-p656
CVE: CVE-2017-16088
CWE: CWE-610
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-ww6v-677g-p656
Type: github-advisory

## Affected
- npm: `safe-eval` — affected >=0

## Details
Affected versions of `safe-eval` are vulnerable to a sandbox escape. By accessing object constructors, un-sanitized user input can access the entire standard library and effectively break out of the sandbox. 

## Proof of Concept:
This code accesses the process object and calls `.exit()`
```js
var safeEval = require('safe-eval');
safeEval("this.constructor.constructor('return process')().exit()");
```


## Recommendation

Update to version 0.4.0 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16088
- https://github.com/hacksparrow/safe-eval/issues/5
- https://github.com/patriksimek/vm2/issues/59
- https://github.com/hacksparrow/safe-eval/pull/13
- https://github.com/advisories/GHSA-ww6v-677g-p656
- https://www.npmjs.com/advisories/337
