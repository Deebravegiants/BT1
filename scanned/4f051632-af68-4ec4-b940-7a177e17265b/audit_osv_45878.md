# [H] Due to a mistake in libcurl's WebSocket code, a malicious server can send a particularly crafted...

## Summary
Severity: High
Advisory: JLSEC-2026-434
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-434
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.13.0+0 <8.14.1+0
- Julia: `LibCURL_jll` — affected >=8.13.0+0 <8.14.1+0

## Details
Due to a mistake in libcurl's WebSocket code, a malicious server can send a
particularly crafted packet which makes libcurl get trapped in an endless
busy-loop.

There is no other way for the application to escape or exit this loop other
than killing the thread/process.

This might be used to DoS libcurl-using application.

## References
- http://www.openwall.com/lists/oss-security/2025/06/04/2
- https://curl.se/docs/CVE-2025-5399.html
- https://curl.se/docs/CVE-2025-5399.json
- https://github.com/advisories/GHSA-8h93-38hx-vv92
- https://hackerone.com/reports/3168039
- https://nvd.nist.gov/vuln/detail/CVE-2025-5399
