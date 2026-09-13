# [C] Verification Bypass in jsonwebtoken

## Summary
Severity: Critical
Advisory: GHSA-c7hr-j4mj-j2w6
CVE: CVE-2015-9235
CWE: CWE-20
Ecosystem: npm
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-c7hr-j4mj-j2w6
Type: github-advisory

## Affected
- npm: `jsonwebtoken` — affected >=0 <4.2.2

## Details
Versions 4.2.1 and earlier of `jsonwebtoken` are affected by a verification bypass vulnerability. This is a result of weak validation of the JWT algorithm type, occuring when an attacker is allowed to arbitrarily specify the JWT algorithm.




## Recommendation

Update to version 4.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9235
- https://github.com/auth0/node-jsonwebtoken/commit/1bb584bc382295eeb7ee8c4452a673a77a68b687
- https://auth0.com/blog/2015/03/31/critical-vulnerabilities-in-json-web-token-libraries
- https://github.com/advisories/GHSA-c7hr-j4mj-j2w6
- https://www.npmjs.com/advisories/17
- https://www.timmclean.net/2015/02/25/jwt-alg-none.html
