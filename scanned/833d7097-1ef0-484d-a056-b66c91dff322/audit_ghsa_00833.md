# [H] Denial of Service in http-proxy

## Summary
Severity: High
Advisory: GHSA-6x33-pw7p-hmpq
CWE: CWE-184, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-6x33-pw7p-hmpq
Type: github-advisory

## Affected
- npm: `http-proxy` — affected >=0 <1.18.1

## Details
Versions of `http-proxy` prior to 1.18.1 are vulnerable to Denial of Service. An HTTP request with a long body triggers an `ERR_HTTP_HEADERS_SENT` unhandled exception that crashes the proxy server. This is only possible when the proxy server sets headers in the proxy request using the `proxyReq.setHeader` function.   

For a proxy server running on `http://localhost:3000`, the following curl request triggers the unhandled exception:  
```curl -XPOST http://localhost:3000 -d "$(python -c 'print("x"*1025)')"```


## Recommendation

Upgrade to version 1.18.1 or later

## References
- https://github.com/http-party/node-http-proxy/pull/1447/commits/4718119ffbe895aecd9be0d6430357d44b4c7fd3
- https://github.com/http-party/node-http-proxy/pull/1447/files
- https://www.npmjs.com/advisories/1486
