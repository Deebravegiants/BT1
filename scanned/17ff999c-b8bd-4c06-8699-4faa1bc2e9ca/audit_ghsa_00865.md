# [H] Insecure Default Configuration in graphql-code-generator

## Summary
Severity: High
Advisory: GHSA-9w87-4j72-gcv7
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-9w87-4j72-gcv7
Type: github-advisory

## Affected
- npm: `graphql-code-generator` — affected >=0 <0.18.2

## Details
Versions of `graphql-code-generator` prior to 0.18.2 have an Insecure Default Configuration. The packages sets `NODE_TLS_REJECT_UNAUTHORIZED` to 0, disabling certificate verification for the entire project. This results in Insecure Communication for the process.


## Recommendation

Upgrade to version 0.18.2 or later.

## References
- https://github.com/dotansimha/graphql-code-generator/issues/1806
- https://www.npmjs.com/advisories/834
