# [C] Improper Authorization in passport-cognito

## Summary
Severity: Critical
Advisory: GHSA-v6c5-hwqg-3x5q
CVE: CVE-2019-19723
CWE: CWE-285
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-v6c5-hwqg-3x5q
Type: github-advisory

## Affected
- npm: `passport-cognito` — affected >=0.0.0

## Details
All versions of `passport-cognito` are vulnerable to Improper Authorization. The package fails to properly scope the variables containing authorization information, such as access token, refresh token and ID token. This causes a race condition where simultaneous authenticated users may receive authorization tokens for a different user. This would allow a user to take actions on another user's behalf.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19723
- https://www.npmjs.com/advisories/1443
