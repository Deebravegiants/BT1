# [H] Denial of Service in hapi

## Summary
Severity: High
Advisory: GHSA-rc8h-3fv6-pxv8
CVE: CVE-2015-9241
CWE: CWE-400
Ecosystem: npm
Published: 2018-06-07
Source: https://github.com/advisories/GHSA-rc8h-3fv6-pxv8
Type: github-advisory

## Affected
- npm: `hapi` — affected >=0 <11.1.3

## Details
Versions of `hapi` prior to 11.1.3 are affected by a denial of service vulnerability.

The vulnerability is triggered when certain input is passed into the If-Modified-Since or Last-Modified headers.

This causes an 'illegal access' exception to be raised, and instead of sending a HTTP 500 error back to the sender, hapi will continue to hold the socket open until timed out (default node timeout is 2 minutes).





## Recommendation

Update to v11.1.3 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9241
- https://github.com/jfhbrook/node-ecstatic/pull/179
- https://github.com/hapijs/hapi/commit/aab2496e930dce5ee1ab28eecec94e0e45f03580
- https://github.com/advisories/GHSA-rc8h-3fv6-pxv8
- https://www.npmjs.com/advisories/63
