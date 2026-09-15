# [H] Prototype Pollution in reggae

## Summary
Severity: High
Advisory: GHSA-q9wr-gcjc-hq52
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-q9wr-gcjc-hq52
Type: github-advisory

## Affected
- npm: `reggae` — affected >=0.0.0

## Details
All versions of `reggae` are vulnerable to prototype pollution. The function `set` does not restrict the modification of an Object's prototype, which may allow a malicious to add or modify an existing property that will exist on all objects.




## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1331
