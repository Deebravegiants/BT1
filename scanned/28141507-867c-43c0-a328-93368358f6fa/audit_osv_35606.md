# [H] QUIC zero-length UDP datagrams busy-loop

## Summary
Severity: High
Advisory: CVE-2026-11352
Aliases: CURL-CVE-2026-11352
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-03
Source: https://osv.dev/vulnerability/CVE-2026-11352
Type: osv

## Details
An issue in curl’s QUIC UDP receive function allows a malicious HTTP/3 server
to trigger a remote denial of service against a curl or libcurl client.
Because the helper function discards zero-length UDP datagrams before counting
them toward the per-call packet budget, a connected QUIC peer can continuously
stream empty datagrams to indefinitely stall the client.

## References
- https://curl.se/docs/CVE-2026-11352.html
- https://curl.se/docs/CVE-2026-11352.json
- https://hackerone.com/reports/3783438
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11352.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11352
