# [H] Prototype Pollution in querystringify

## Summary
Severity: High
Advisory: GHSA-hxcm-v35h-mg2x
CWE: CWE-1321
Ecosystem: npm
Published: 2019-06-07
Source: https://github.com/advisories/GHSA-hxcm-v35h-mg2x
Type: github-advisory

## Affected
- npm: `querystringify` — affected >=0 <2.0.0

## Details
A vulnerability was found in querystringify before 2.0.0. It's possible to override built-in properties of the resulting query string object if a malicious string is inserted in the query string.

## References
- https://github.com/unshiftio/querystringify/pull/19
- https://github.com/unshiftio/querystringify/commit/422eb4f6c7c28ee5f100dcc64177d3b68bb2b080
