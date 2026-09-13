# [H] Denial of Service in ecstatic

## Summary
Severity: High
Advisory: GHSA-vwjc-q9px-r9vq
CVE: CVE-2015-9242
CWE: CWE-400
Ecosystem: npm
Published: 2018-06-07
Source: https://github.com/advisories/GHSA-vwjc-q9px-r9vq
Type: github-advisory

## Affected
- npm: `ecstatic` — affected >=0 <1.4.0

## Details
Versions of `ecstatic` prior to 1.4.0 are affected by a denial of service vulnerability when certain input strings are sent via the `Last-Modified` or `If-Modified-Since` headers.

Parsing certain inputs with `new Date()` or `Date.parse()` cases v8 to crash. As ecstatic passes the value of the affected headers into one of these functions, sending certain inputs via one of the headers will cause the server to crash.



## Recommendation

Update to version 1.4.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9242
- https://github.com/jfhbrook/node-ecstatic/pull/179
- https://github.com/jfhbrook/node-ecstatic/commit/0d0a2779ac5e5843d3745920212dfac9b69440e2
- https://bugs.chromium.org/p/v8/issues/detail?id=4640
- https://github.com/jfhbrook/node-ecstatic
