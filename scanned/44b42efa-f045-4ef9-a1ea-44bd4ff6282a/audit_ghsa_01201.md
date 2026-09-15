# [M] Unsafe Merging of CORS Configuration Conflict in hapi

## Summary
Severity: Medium
Advisory: GHSA-j3g2-m5jj-6336
CVE: CVE-2015-9243
CWE: CWE-284
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-j3g2-m5jj-6336
Type: github-advisory

## Affected
- npm: `hapi` — affected >=0 <11.1.4

## Details
Versions of `hapi` prior to 11.1.4 are affected by a vulnerability that causes route-level CORS configuration to override connection-level or server-level CORS defaults. This may result in a situation where CORS permissions are less restrictive than intended.




## Recommendation

Update hapi to version 11.1.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9243
- https://github.com/hapijs/hapi/issues/2980
- https://www.npmjs.com/advisories/65
