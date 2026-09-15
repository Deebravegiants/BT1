# [C] Remote Code Execution in mongodb-query-parser

## Summary
Severity: Critical
Advisory: GHSA-97mg-3cr6-3x4c
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-97mg-3cr6-3x4c
Type: github-advisory

## Affected
- npm: `mongodb-query-parser` — affected >=0 <2.0.0

## Details
Versions of `mongodb-query-parser` prior to 2.0.0 are vulnerable to Remote Code Execution. The package fails to sanitize queries, allowing attackers to execute arbitrary code in the system.  Parsing the following payload executes `touch test-file`: 

```'(function () { return (clearImmediate.constructor("return process;")()).mainModule.require("child_process").execSync("touch test-file").toString()})()'```



## Recommendation

Upgrade to version 2.0.0 or later.

## References
- https://www.npmjs.com/advisories/1448
