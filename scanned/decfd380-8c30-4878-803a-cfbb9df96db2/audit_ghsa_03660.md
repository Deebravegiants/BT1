# [H] Cross-Site Scripting (XSS) in cloudcmd

## Summary
Severity: High
Advisory: GHSA-m8fw-534v-xm85
CWE: CWE-79
Ecosystem: npm
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-m8fw-534v-xm85
Type: github-advisory

## Affected
- npm: `cloudcmd` — affected >=0 <9.1.6

## Details
Versions of `cloudcmd` before 9.1.6 are vulnerable to cross-site scripting (XSS) when listing files in a directory. The attacker must control the name of a file for this vulnerability to be exploitable.


## Recommendation

Update to version 9.1.6 or later.

## References
- https://github.com/coderaiser/cloudcmd/commit/23f4d4702cd3d473977285f26ea2ae7206b45f38
- https://hackerone.com/reports/341044
- https://hackerone.com/reports/341044)
- https://www.npmjs.com/advisories/642
