# [C] libre: Integer overflow in websock_decode() masked frame length check leads to heap buffer overflow

## Summary
Severity: Critical
Advisory: CVE-2026-50161
Aliases: GHSA-hvxv-v2gp-v93h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-50161
Type: osv

## Details
libre is a generic library for real-time communications with asynchronous input and output support. Prior to 4.8.1, the websock_decode() function in src/websock/websock.c contains an integer overflow when validating a masked WebSocket frame that uses the 64-bit extended length encoding. The expression 4 + hdr->len can wrap when hdr->len is close to UINT64_MAX, causing the mbuf_get_left() bounds check to pass. The subsequent XOR unmasking loop then writes beyond the heap buffer. Applications using websock_accept() or websock_accept_proto() to implement a WebSocket server are affected, and exploitation can cause attacker-controlled heap corruption or denial of service after the HTTP WebSocket upgrade handshake. This issue is fixed in version 4.8.1.

## References
- https://github.com/baresip/re/releases/tag/v4.8.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50161.json
- https://github.com/baresip/re/security/advisories/GHSA-hvxv-v2gp-v93h
- https://nvd.nist.gov/vuln/detail/CVE-2026-50161
- https://github.com/baresip/re/commit/718b92615c7963670d26c1a2b246968b58d782e8
- https://github.com/baresip/re/pull/1584
