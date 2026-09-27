# [C] Command Injection in ps-kill

## Summary
Severity: Critical
Advisory: GHSA-7qmm-q394-fmch
CVE: CVE-2021-23355
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-7qmm-q394-fmch
Type: github-advisory

## Affected
- npm: `ps-kill` — affected >=0

## Details
This affects all versions of package ps-kill. If (attacker-controlled) user input is given to the kill function, it is possible for an attacker to execute arbitrary commands. This is due to use of the child_process exec function without input sanitization in the index.js file. 

PoC (provided by reporter): 
```js
var ps_kill = require('ps-kill');
ps_kill.kill('$(touch success)', function() {});
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23355
- https://snyk.io/vuln/SNYK-JS-PSKILL-1078529
