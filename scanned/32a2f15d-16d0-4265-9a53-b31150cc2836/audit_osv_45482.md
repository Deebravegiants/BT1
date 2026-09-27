# [C] When reusing a libcurl handle for sequential transfers driven by environment-variable proxy...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1216
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1216
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.21.0+0

## Details
When reusing a libcurl handle for sequential transfers driven by
environment-variable proxy configuration, libcurl fails to clear the proxy
authentication state between requests. Specifically, if the initial transfer
authenticates against `proxyA` using Digest auth, a subsequent transfer routed
through `proxyB` erroneously leaks the `Proxy-Authorization:` header intended
solely for `proxyA`.

## References
- https://curl.se/docs/CVE-2026-8927.html
- https://curl.se/docs/CVE-2026-8927.json
- https://github.com/advisories/GHSA-jr4f-4564-w3mr
- https://hackerone.com/reports/3744543
- https://nvd.nist.gov/vuln/detail/CVE-2026-8927
