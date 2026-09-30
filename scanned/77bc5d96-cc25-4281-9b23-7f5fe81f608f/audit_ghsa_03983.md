# [C] Authentication Bypass in hapi-auth-jwt2

## Summary
Severity: Critical
Advisory: GHSA-mg8r-9g6j-hwv9
CVE: CVE-2016-10525
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-mg8r-9g6j-hwv9
Type: github-advisory

## Affected
- npm: `hapi-auth-jwt2` — affected >=5.1.1 <5.1.2

## Details
Versions of `hapi-auth-jwt2` prior to version 5.1.2 are affected by a complete authentication bypass vulnerability when in the `try` authentication mode. 


## Recommendation

Update to version 5.1.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10525
- https://github.com/dwyl/hapi-auth-jwt2/issues/111
- https://github.com/dwyl/hapi-auth-jwt2/pull/112
- https://github.com/advisories/GHSA-mg8r-9g6j-hwv9
- https://github.com/dwyl/hapi-auth-jwt2
- https://www.npmjs.com/advisories/81
