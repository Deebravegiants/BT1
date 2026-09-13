# [C] Path Traversal in sapper

## Summary
Severity: Critical
Advisory: GHSA-f3vw-587g-r29g
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-f3vw-587g-r29g
Type: github-advisory

## Affected
- npm: `sapper` — affected >=0 <0.27.11

## Details
Versions of `sapper` prior to 0.27.11 are vulnerable to Path Traversal. It is possible to access sensitive files on the server through HTTP requests containing URL-encoded `../`.  

You may test a `sapper` application running in prod mode with `curl -vvv http://localhost:3000/client/750af05c3a69ddc6073a/%252e%252e/%252e%252e/%252e%252e/%252e%252e/%252e%252e/%252e%252e/%252e%252e/%252e%252e/etc/passwd`.


## Recommendation

Upgrade to version 0.27.11 or later.

## References
- https://www.npmjs.com/advisories/1494
