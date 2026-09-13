# [H] Prototype Pollution in mixme

## Summary
Severity: High
Advisory: GHSA-84p7-fh9c-6g8h
CWE: CWE-1321
Ecosystem: npm
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-84p7-fh9c-6g8h
Type: github-advisory

## Affected
- npm: `mixme` — affected >=0 <0.5.2

## Details
### Impact
When copying properties from a source object to a target object, the target object can gain access to certain properties of the source object and modify their content.

### Patches
The problem was patch with a more agressive discovery of secured properties to filter out.

## References
- https://github.com/adaltas/node-mixme/security/advisories/GHSA-84p7-fh9c-6g8h
- https://github.com/adaltas/node-mixme/issues/1
- https://github.com/adaltas/node-mixme/issues/2
- https://github.com/adaltas/node-mixme/commit/db70fe9bcbba451e9f8bd794a9fa7cdfa00125ad
- https://github.com/adaltas/node-mixme
- https://github.com/advisories/GHSA-79jw-6wg7-r9g4
