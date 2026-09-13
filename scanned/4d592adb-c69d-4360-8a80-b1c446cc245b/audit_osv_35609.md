# [M] Cesanta Mongoose Out-of-Bounds Read in MG_TLS_BUILTIN ClientHello Session ID Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-11404
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-11404
Type: osv

## Details
Cesanta Mongoose before 7.22 contains an out-of-bounds read in the built-in TLS server function mg_tls_server_recv_hello(), which uses an attacker-controlled session_id_len byte from a TLS ClientHello as a buffer index without validating it against the length of received data. A remote, unauthenticated attacker can send a single crafted ClientHello with an oversized session id length to read past the receive buffer, crashing any HTTPS, MQTTS, or WSS service built on MG_TLS_BUILTIN.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11404.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-11404
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://github.com/cesanta/mongoose
