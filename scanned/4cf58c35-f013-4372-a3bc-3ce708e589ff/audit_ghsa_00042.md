# [M] Incorrect handling of CORS preflight request headers in hapi

## Summary
Severity: Medium
Advisory: GHSA-vwrf-r5r4-7775
CVE: CVE-2015-9236
CWE: CWE-284
Ecosystem: npm
Published: 2018-06-07
Source: https://github.com/advisories/GHSA-vwrf-r5r4-7775
Type: github-advisory

## Affected
- npm: `hapi` — affected >=0 <11.0.0

## Details
Versions of `hapi` prior to 11.0.0 implement CORS incorrectly, allowing for configurations that at best return inconsistent headers, and at worst allow cross-origin activities that are expected to be forbidden. 

If the connection has CORS enabled but one route has it off, and the route is not GET, the OPTIONS prefetch request will return the default CORS headers and then the actual request will go through and return no CORS headers. This defeats the purpose of turning CORS on the route.


## Recommendation

Update to version 11.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9236
- https://github.com/hapijs/hapi/issues/2840
- https://github.com/hapijs/hapi/issues/2850
- https://github.com/advisories/GHSA-vwrf-r5r4-7775
- https://www.npmjs.com/advisories/45
