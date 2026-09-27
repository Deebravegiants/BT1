# [H] DoS due to excessively large websocket message in ws

## Summary
Severity: High
Advisory: GHSA-6663-c963-2gqg
CVE: CVE-2016-10542
CWE: CWE-400
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-6663-c963-2gqg
Type: github-advisory

## Affected
- npm: `ws` — affected >=0 <1.1.1

## Details
Affected versions of `ws` do not appropriately limit the size of incoming websocket payloads, which may result in a denial of service condition when the node process crashes after receiving a large payload.



## Recommendation

Update to version 1.1.1 or later. 
Alternatively, set the `maxpayload` option for the `ws` server to a value smaller than 256MB.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10542
- https://github.com/nodejs/node/issues/7388
- https://github.com/advisories/GHSA-6663-c963-2gqg
- https://www.npmjs.com/advisories/120
