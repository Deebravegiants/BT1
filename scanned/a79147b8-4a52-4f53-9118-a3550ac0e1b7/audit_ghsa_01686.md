# [C] Command Injection in hot-formula-parser

## Summary
Severity: Critical
Advisory: GHSA-rc77-xxq6-4mff
CVE: CVE-2020-6836
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-06
Source: https://github.com/advisories/GHSA-rc77-xxq6-4mff
Type: github-advisory

## Affected
- npm: `hot-formula-parser` — affected >=0 <3.0.1

## Details
Versions of `hot-formula-parser` prior to 3.0.1 are vulnerable to Command Injection. The package fails to sanitize values passed to the  `parse` function and concatenates it in an `eval` call. If a value of the formula is supplied by user-controlled input it may allow attackers to run arbitrary commands in the server.  
Parsing the following formula creates a `test` file in the present directory:  
`"SUM([(function(){require('child_process').execSync('touch test')})(),2])"`


## Recommendation

Upgrade to version 3.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-6836
- https://github.com/handsontable/formula-parser/pull/58
- https://github.com/handsontable/formula-parser/commit/396b089738d4bf30eb570a4fe6a188affa95cd5e
- https://blog.truesec.com/2020/01/17/reverse-shell-through-a-node-js-math-parser
- https://github.com/handsontable/formula-parser
- https://www.npmjs.com/advisories/1439
