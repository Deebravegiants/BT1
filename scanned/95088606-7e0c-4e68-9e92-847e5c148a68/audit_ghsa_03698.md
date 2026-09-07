# [H] Command Injection in wiki-plugin-datalog

## Summary
Severity: High
Advisory: GHSA-pm52-wwrw-c282
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-pm52-wwrw-c282
Type: github-advisory

## Affected
- npm: `wiki-plugin-datalog` — affected >=0 <0.1.6

## Details
Versions of `wiki-plugin-datalog` prior to 0.1.6 are vulnerable to Command Injection. The package failed to sanitize URLs on the curl endpoint, allowing attackers to inject commands and possibly achieving Remote Code Execution on the system.


## Recommendation

Upgrade to version 0.1.6 or later.

## References
- https://github.com/WardCunningham/wiki-plugin-datalog/commit/020aa6201319e5b76301a61b65268c94dc242fa7
- https://snyk.io/vuln/SNYK-JS-WIKIPLUGINDATALOG-449540
- https://www.npmjs.com/advisories/926
