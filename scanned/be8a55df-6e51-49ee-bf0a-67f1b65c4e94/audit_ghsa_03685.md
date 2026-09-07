# [M] Rate Limiting Bypass in express-brute

## Summary
Severity: Medium
Advisory: GHSA-984p-xq9m-4rjw
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-06-07
Source: https://github.com/advisories/GHSA-984p-xq9m-4rjw
Type: github-advisory

## Affected
- npm: `express-brute` — affected >=0

## Details
All versions of `express-brute` are vulnerable to Rate Limiting Bypass. Concurrent requests may lead to race conditions that cause the package to incorrectly count requests. This may allow an attacker to bypass the rate limiting provided by the package and execute requests without limiting.


## Recommendation

No fix is currently available. Consider using an alternative module until a fix is made available.

## References
- https://github.com/AdamPflug/express-brute/issues/46
- https://snyk.io/vuln/SNYK-JS-EXPRESSBRUTE-174457
- https://www.npmjs.com/advisories/823
