# [H] Denial of Service in uws

## Summary
Severity: High
Advisory: GHSA-hf5h-hh56-3vrg
CVE: CVE-2016-10544
CWE: CWE-400
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-hf5h-hh56-3vrg
Type: github-advisory

## Affected
- npm: `uws` — affected >=0.10.0 <0.10.9

## Details
Affected versions of `uws` do not properly handle large websocket messages when `permessage-deflate` is enabled, which may result in a denial of service condition.

If `uws` recieves a 256Mb websocket message when `permessage-deflate` is enabled, the server will compress the message prior to executing the length check, and subsequently extract the message prior to processing. This can result in a situation where an excessively large websocket message passes the length checks, yet still gets cast from a Buffer to a string, which will exceed v8's maximum string size and crash the process.


## Recommendation

Update to version 0.10.9 or later.

Alternatively, disable `permessage-deflate`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10544
- https://github.com/uWebSockets/uWebSockets/commit/37deefd01f0875e133ea967122e3a5e421b8fcd9
- https://www.npmjs.com/advisories/149
