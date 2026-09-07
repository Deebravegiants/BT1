# [M] CORS Token Disclosure in crumb

## Summary
Severity: Medium
Advisory: GHSA-84fq-6626-w5fg
CVE: CVE-2014-7193
CWE: CWE-284
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-84fq-6626-w5fg
Type: github-advisory

## Affected
- npm: `crumb` — affected >=0 <3.0.0

## Details
When CORS is enabled on a hapi route handler, it is possible to set a crumb token for a different domain. An attacker would need to have an application consumer visit a site they control, request a route supporting CORS, and then retrieve the token. With this token, they could possibly make requests to non CORS routes as this user.

A configuration and scenario where this would occur is unlikely, as most configurations will set CORS globally (where crumb is not used), or not at all.


## Recommendation

Update to version 3.0.0 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-7193
- https://github.com/hapijs/crumb/commit/5e6d4f5c81677fe9e362837ffd4a02394303db3c
- https://github.com/spumko/crumb/commit/5e6d4f5c81677fe9e362837ffd4a02394303db3c
- https://github.com/advisories/GHSA-84fq-6626-w5fg
- https://www.npmjs.com/advisories/4
