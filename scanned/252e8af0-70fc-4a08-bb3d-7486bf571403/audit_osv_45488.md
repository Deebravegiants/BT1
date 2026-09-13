# [H] A vulnerability in libcurl caused the HTTP `Referer:` header to persist even when explicitly...

## Summary
Severity: High
Advisory: JLSEC-2026-1221
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1221
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.20.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.18.0+0 <8.21.0+0

## Details
A vulnerability in libcurl caused the HTTP `Referer:` header to persist even
when explicitly cleared. While the documentation states that passing NULL to
`CURLOPT_REFERER` suppresses the header, the option failed to clear the
internal state. As a result the previous referrer string was erroneously
reused and sent in subsequent requests, potentially leaking sensitive
information to unintended servers.

## References
- https://curl.se/docs/CVE-2026-9546.html
- https://curl.se/docs/CVE-2026-9546.json
- https://github.com/advisories/GHSA-25rx-86v8-32c6
- https://hackerone.com/reports/3754343
- https://nvd.nist.gov/vuln/detail/CVE-2026-9546
