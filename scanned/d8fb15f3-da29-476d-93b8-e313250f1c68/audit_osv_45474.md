# [H] Using libcurl, when a custom `Host:` header is first set for an HTTP request and a second request...

## Summary
Severity: High
Advisory: JLSEC-2026-1207
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1207
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.20.0+0
- Julia: `LibCURL_jll` — affected >=7.71.1+0 <8.20.0+0

## Details
Using libcurl, when a custom `Host:` header is first set for an HTTP request
and a second request is subsequently done using the same *easy handle* but
without the custom `Host:` header set, the second request would use stale
information and pass on cookies meant for the first host in the second
request. Leak them.

## References
- http://www.openwall.com/lists/oss-security/2026/04/29/13
- https://curl.se/docs/CVE-2026-6276.html
- https://curl.se/docs/CVE-2026-6276.json
- https://github.com/advisories/GHSA-2jc6-hc33-hv48
- https://hackerone.com/reports/3671818
- https://nvd.nist.gov/vuln/detail/CVE-2026-6276
