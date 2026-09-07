# [M] Remote Memory Exposure in floody

## Summary
Severity: Medium
Advisory: GHSA-3p92-886g-qxpq
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-3p92-886g-qxpq
Type: github-advisory

## Affected
- npm: `floody` — affected >=0 <0.1.1

## Details
Versions of `floody` before 0.1.1 are vulnerable to remote memory exposure.

.write(number)` in the affected `floody` versions passes a number to Buffer constructor, appending a chunk of uninitialized memory.

Proof of Concept: 

```
var f = require('floody')(process.stdout); 
f.write(USERSUPPLIEDINPUT); 
'f.stop();


## Recommendation

Update to version 0.1.1 or later.

## References
- https://github.com/soldair/node-floody/commit/6c44722312131f4ac8a1af40f0f861c85efe01b0
- https://snyk.io/vuln/npm:floody:20160115
- https://www.npmjs.com/advisories/601
