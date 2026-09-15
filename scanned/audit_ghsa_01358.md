# [H] Prototype Pollution in @commercial/subtext

## Summary
Severity: High
Advisory: GHSA-36c4-4r89-6whg
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-36c4-4r89-6whg
Type: github-advisory

## Affected
- npm: `@commercial/subtext` — affected >=0 <5.1.2

## Details
Versions of `@commercial/subtext` prior to 5.1.2 are vulnerable to Prototype Pollution. A multipart payload can be constructed in a way that one of the parts’ content can be set as the entire payload object’s prototype. If this prototype contains data, it may bypass other validation rules which enforce access and privacy. If this prototype evaluates to null, it can cause unhandled exceptions when the request payload is accessed.


## Recommendation

Upgrade to version 5.1.2 or later.

## References
- https://www.npmjs.com/advisories/1484
