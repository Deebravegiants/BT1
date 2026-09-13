# [C] libcurl keeps previously used connections in a connection pool for subsequent transfers to reuse...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1199
Ecosystem: Julia
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1199
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.17.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.17.0+0 <8.21.0+0

## Details
libcurl keeps previously used connections in a connection pool for subsequent
transfers to reuse if one of them matches the setup.

An easy handle that first uses default native CA trust can continue trusting
the native platform store after the application switches that same handle to
custom CA material for a later transfer.

## References
- https://curl.se/docs/CVE-2026-11564.html
- https://curl.se/docs/CVE-2026-11564.json
- https://github.com/advisories/GHSA-hf82-6jff-f22v
- https://hackerone.com/reports/3788984
- https://nvd.nist.gov/vuln/detail/CVE-2026-11564
