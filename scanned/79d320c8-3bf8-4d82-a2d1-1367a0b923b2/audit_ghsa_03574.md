# [M] Weak JSON Web Token in yapi-vendor

## Summary
Severity: Medium
Advisory: GHSA-2h3h-vw8r-82rp
CVE: CVE-2021-27884
CWE: CWE-330
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-26
Source: https://github.com/advisories/GHSA-2h3h-vw8r-82rp
Type: github-advisory

## Affected
- npm: `yapi-vendor` — affected >=0 <1.9.3

## Details
Weak JSON Web Token (JWT) signing secret generation in YMFE YApi through 1.9.2 allows recreation of other users' JWT tokens. This occurs because Math.random in Node.js is used as a source of randomness in jwt signing. Math.random does not provide cryptographically secure random numbers. This has been patched in version 1.9.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27884
- https://github.com/YMFE/yapi/issues/2117
- https://github.com/YMFE/yapi/issues/2263
- https://securitylab.github.com/advisories/GHSL-2020-228-YMFE-yapi
