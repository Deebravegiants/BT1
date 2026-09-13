# [M] Cesanta Mongoose before 7.22 contains an out-of-bounds read in the built-in TLS server function...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1257
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1257
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected unspecified

## Details
Cesanta Mongoose before 7.22 contains an out-of-bounds read in the built-in TLS server function `mg_tls_server_recv_hello()`, which uses an attacker-controlled `session_id_len` byte from a TLS ClientHello as a buffer index without validating it against the length of received data. A remote, unauthenticated attacker can send a single crafted ClientHello with an oversized session id length to read past the receive buffer, crashing any HTTPS, MQTTS, or WSS service built on `MG_TLS_BUILTIN`.

## References
- https://github.com/advisories/GHSA-cvgj-gr8r-q762
- https://github.com/cesanta/mongoose
- https://github.com/cesanta/mongoose/commit/c288ac1f38424ffdd4d2fd5e1893fd4962642db3
- https://github.com/cesanta/mongoose/releases/tag/7.22
- https://nvd.nist.gov/vuln/detail/CVE-2026-11404
- https://www.vulncheck.com/advisories/cesanta-mongoose-out-of-bounds-read-in-mg-tls-builtin-clienthello-session-id-parsing
