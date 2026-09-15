# [C] The curl logic that works with SASL authentication could end up cleaning up the GSASL context ...

## Summary
Severity: Critical
Advisory: JLSEC-2026-1214
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1214
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.16.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.15.0+0 <8.21.0+0

## Details
The curl logic that works with SASL authentication could end up cleaning up
the GSASL context *twice* without clearing the pointer in between, making it
`free()` the same pointer twice.

## References
- https://curl.se/docs/CVE-2026-8925.html
- https://curl.se/docs/CVE-2026-8925.json
- https://github.com/advisories/GHSA-p8x5-c6c9-8cwx
- https://hackerone.com/reports/3735193
- https://nvd.nist.gov/vuln/detail/CVE-2026-8925
