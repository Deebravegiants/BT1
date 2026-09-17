# [H] WS Auto-PONG memory exhaustion

## Summary
Severity: High
Advisory: CVE-2026-11586
Aliases: CURL-CVE-2026-11586
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-11586
Type: osv

## Details
By default, curl automatically responds to WebSocket PING frames. Because curl
lacks an upper bound on memory allocation for unacknowledged frames, a
malicious server can exhaust all available memory by flooding curl with rapid,
sequential PING messages.

## References
- https://curl.se/docs/CVE-2026-11586.html
- https://curl.se/docs/CVE-2026-11586.json
- https://hackerone.com/reports/3788931
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11586.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11586
