# [H] Libevent: Heap out-of-bounds write in bufferevent_socket_set_conn_address_ reachable via AF_UNIX accept

## Summary
Severity: High
Advisory: CVE-2026-63388
Aliases: GHSA-cvq5-vrvr-j338
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-63388
Type: osv

## Details
Libevent is an event notification library. Prior to 2.1.13 and 2.2.2-alpha, libevent has a heap out-of-bounds write in bufferevent_sock.c when bufferevent_socket_set_conn_address_ copies a kernel-supplied AF_UNIX peer address into bufferevent_private.conn_address. Release builds compiled with NDEBUG disable the EVUTIL_ASSERT length guard, and the evhttp accept path can pass a 110-byte sockaddr from accept() into the 28-byte field. An unauthenticated local peer able to connect to an AF_UNIX listener can overwrite the adjacent dns_request pointer and heap data, causing memory corruption with confidentiality, integrity, and availability impact. This issue is fixed in versions 2.1.13 and 2.2.2-alpha.

## References
- https://github.com/libevent/libevent/releases/tag/release-2.1.13-stable
- https://github.com/libevent/libevent/releases/tag/release-2.2.2-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63388.json
- https://github.com/libevent/libevent/security/advisories/GHSA-cvq5-vrvr-j338
- https://nvd.nist.gov/vuln/detail/CVE-2026-63388
- https://github.com/libevent/libevent/commit/52057cb33d0c20c0a0453fbabe6c0c96854931b9
- https://github.com/libevent/libevent/commit/ef38f926e9cd1f082416c6fff13587bc1f431d72
