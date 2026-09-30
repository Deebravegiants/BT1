# [M] coturn allocates a full per-peer SSL/session before verifying the DTLS cookie, enabling source-spoofing/botnet state-exhaustion DoS

## Summary
Severity: Medium
Advisory: CVE-2026-73214
Aliases: GHSA-5x2p-4vqj-f6m4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73214
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.16.0, dtls_server_input_handler() and create_new_connected_udp_socket() in src/apps/relay/dtls_listener.c retain OpenSSL dtls1_reassemble_fragment() state for a 35-byte fragmented ClientHello declaring a 650,000-byte handshake before cookie validation, allowing an unauthenticated remote sender using fresh UDP tuples to exhaust memory without TURN credentials, a completed handshake, a valid cookie, or source spoofing. This issue is fixed in version 4.16.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.16.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73214.json
- https://github.com/coturn/coturn/security/advisories/GHSA-5x2p-4vqj-f6m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-73214
- https://github.com/coturn/coturn/commit/37e13d1d60af8f1422c01b5e9f1c6bc355d03b85
- https://github.com/coturn/coturn/commit/beb4de9dcb6a475129595b943c9a34264420df09
- https://github.com/coturn/coturn/pull/2003
- https://github.com/coturn/coturn/pull/2012
