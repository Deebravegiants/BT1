# [M] Coturn: uint16_t truncation overflow in STUN message length causes TCP stream framing bypass

## Summary
Severity: Medium
Advisory: CVE-2026-68552
Aliases: GHSA-m562-mf7x-q7rr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-68552
Type: osv

## Details
Coturn is a free open source implementation of TURN and STUN Server. Prior to 4.15.0, an unauthenticated remote client can send a STUN message over TCP or TLS with a body-length field from 65520 through 65532, causing the uint16_t len variable in stun_get_message_len_str() in src/client/ns_turn_msg.c to wrap when STUN_HEADER_LENGTH is added. The framing layer then consumes only 4 through 16 bytes, treats the remaining bytes as another message, desynchronizes the stream parser, and drops the attacking client's connection. Other clients and the server process are not affected. This issue is fixed in version 4.15.0.

## References
- https://github.com/coturn/coturn/releases/tag/4.15.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68552.json
- https://github.com/coturn/coturn/security/advisories/GHSA-m562-mf7x-q7rr
- https://nvd.nist.gov/vuln/detail/CVE-2026-68552
- https://github.com/coturn/coturn/commit/ed32e1fb6c843f9cf9a28d91c541dfbf40874f25
- https://github.com/coturn/coturn/pull/1964
