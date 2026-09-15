# [H] Code Injection in js-yaml

## Summary
Severity: High
Advisory: GHSA-8j8c-7jfh-h6hx
CWE: CWE-94
Ecosystem: npm
Published: 2019-06-04
Source: https://github.com/advisories/GHSA-8j8c-7jfh-h6hx
Type: github-advisory

## Affected
- npm: `js-yaml` — affected >=0 <3.13.1

## Details
Versions of `js-yaml` prior to 3.13.1 are vulnerable to Code Injection. The `load()` function may execute arbitrary code injected through a malicious YAML file. Objects that have `toString` as key, JavaScript code as value and are used as explicit mapping keys allow attackers to execute the supplied code through the `load()` function. The `safeLoad()` function is unaffected.

An example payload is 
`{ toString: !<tag:yaml.org,2002:js/function> 'function (){return Date.now()}' } : 1` 
which returns the object 
{
  "1553107949161": 1
}


## Recommendation

Upgrade to version 3.13.1.

## References
- https://github.com/nodeca/js-yaml/pull/480
- https://github.com/nodeca/js-yaml/pull/480/commits/e18afbf1edcafb7add2c4c7b22abc8d6ebc2fa61
- https://www.npmjs.com/advisories/813
