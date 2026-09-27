# [H] By default, curl automatically responds to WebSocket PING frames. Because curl lacks an upper...

## Summary
Severity: High
Advisory: JLSEC-2026-1200
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/JLSEC-2026-1200
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.16.0+0 <8.21.0+0
- Julia: `LibCURL_jll` — affected >=8.16.0+0 <8.21.0+0

## Details
By default, curl automatically responds to WebSocket PING frames. Because curl
lacks an upper bound on memory allocation for unacknowledged frames, a
malicious server can exhaust all available memory by flooding curl with rapid,
sequential PING messages.

## References
- https://curl.se/docs/CVE-2026-11586.html
- https://curl.se/docs/CVE-2026-11586.json
- https://github.com/advisories/GHSA-c68q-h477-5646
- https://hackerone.com/reports/3788931
- https://nvd.nist.gov/vuln/detail/CVE-2026-11586
