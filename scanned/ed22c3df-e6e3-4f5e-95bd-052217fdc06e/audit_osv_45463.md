# [H] An issue in curl’s QUIC UDP receive function allows a malicious HTTP/3 server to trigger a remote...

## Summary
Severity: High
Advisory: JLSEC-2026-1198
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1198
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.20.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.18.0+0 <8.21.0+0

## Details
An issue in curl’s QUIC UDP receive function allows a malicious HTTP/3 server
to trigger a remote denial of service against a curl or libcurl client.
Because the helper function discards zero-length UDP datagrams before counting
them toward the per-call packet budget, a connected QUIC peer can continuously
stream empty datagrams to indefinitely stall the client.

## References
- https://curl.se/docs/CVE-2026-11352.html
- https://curl.se/docs/CVE-2026-11352.json
- https://github.com/advisories/GHSA-qxwx-hr5v-h5q4
- https://hackerone.com/reports/3783438
- https://nvd.nist.gov/vuln/detail/CVE-2026-11352
