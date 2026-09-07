# [H] silverstripe/graphql Cross-Site Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-wjg9-v8cf-f5q2
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-wjg9-v8cf-f5q2
Type: github-advisory

## Affected
- Packagist: `silverstripe/graphql` — affected >=2.0.0 <2.0.3

## Details
The GraphQL controller lacked any CSRF protection, meaning authenticated users could be forced or tricked into visiting a URL that would send a GET request to the affected web server that could mutate or destroy data without the user knowing.

## References
- https://github.com/silverstripe/silverstripe-graphql/commit/b59ba397ff42d8934bd2d9c932514f898c327f64
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/graphql/SS-2018-007-1.yaml
- https://github.com/silverstripe/silverstripe-graphql
- https://www.silverstripe.org/download/security-releases/ss-2018-007
