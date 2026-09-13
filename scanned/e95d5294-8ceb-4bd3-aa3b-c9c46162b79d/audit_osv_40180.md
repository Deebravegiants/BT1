# [M] net: sockets: tls: Potential out-of-bounds write/read in socket_op_vtable::connect function

## Summary
Severity: Medium
Advisory: CVE-2026-5066
Aliases: GHSA-wgrc-jrf6-24f3
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-5066
Type: osv

## Details
A potential out-of-bounds write/read exists in the TLS socket connect path of the network sockets subsystem (subsys/net/lib/sockets/sockets_tls.c). When the TLS session cache is enabled, tls_session_store() and tls_session_restore() memcpy the caller-supplied address into a fixed-size buffer using the caller-controlled addrlen value without validating it against the destination size. struct net_sockaddr is an opaque type, so an application can pass an addrlen larger than sizeof(struct net_sockaddr) (for example 128 bytes into a 24-byte stack buffer), causing the memcpy to read and write past the end of the address memory used by the TLS session cache. This out-of-bounds write can lead to a crash and denial of service, and potentially to arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5066.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-wgrc-jrf6-24f3
- https://nvd.nist.gov/vuln/detail/CVE-2026-5066
- https://github.com/zephyrproject-rtos/zephyr
