# [H] Prototype Pollution in @hapi/subtext

## Summary
Severity: High
Advisory: GHSA-g9cg-h3jm-cwrc
CWE: CWE-1321
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-g9cg-h3jm-cwrc
Type: github-advisory

## Affected
- npm: `@hapi/pez` — affected >=0 <5.0.1

## Details
Versions of `@hapi/pez` prior to 4.1.2 or 5.0.1 are vulnerable to Prototype Pollution. A multipart payload can be constructed in a way that one of the parts’ content can be set as the entire payload object’s prototype. If this prototype contains data, it may bypass other validation rules which enforce access and privacy. If this prototype evaluates to null, it can cause unhandled exceptions when the request payload is accessed.

## Recommendation

Upgrade to versions 5.0.1 or later. There is a fix available for version 4.1.2,  but it only available for direct download from the repository.

## References
- https://github.com/hapijs/pez
- https://www.npmjs.com/advisories/1480
