# [H] Prototype Pollution in mithril

## Summary
Severity: High
Advisory: GHSA-c3px-v9c7-m734
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-c3px-v9c7-m734
Type: github-advisory

## Affected
- npm: `mithril` — affected >=0 <1.1.7
- npm: `mithril` — affected >=2.0.0 <2.0.2

## Details
Affected versions of `mithril`are vulnerable to prototype pollution. The function `parseQueryString` may allow a malicious user to modify the prototype of `Object`, causing the addition or modification of an existing property that will exist on all objects. A payload such as `__proto__%5BtoString%5D=123` in the query string would change the `toString()` function to `123`.



## Recommendation

If you are using mithril 2.x, upgrade to version 2.0.2 or later.
If you are using mithril 1.x, upgrade to version 1.1.7 or later.

## References
- https://www.npmjs.com/advisories/1094
