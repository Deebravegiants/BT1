# [H] In libssh2 v1.9.0 and earlier versions, the `SSH_MSG_DISCONNECT` logic in packet.c has an integer...

## Summary
Severity: High
Advisory: JLSEC-2025-188
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/JLSEC-2025-188
Type: osv

## Affected
- Julia: `LibSSH2_jll` — affected >=0 <1.10.1+0

## Details
In libssh2 v1.9.0 and earlier versions, the `SSH_MSG_DISCONNECT` logic in packet.c has an integer overflow in a bounds check, enabling an attacker to specify an arbitrary (out-of-bounds) offset for a subsequent memory read. A crafted SSH server may be able to disclose sensitive information or cause a denial of service condition on the client system when a user connects to the server.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00026.html
- http://packetstormsecurity.com/files/172835/libssh2-1.9.0-Out-Of-Bounds-Read.html
- https://blog.semmle.com/libssh2-integer-overflow-CVE-2019-17498/
- https://github.com/kevinbackhouse/SecurityExploits/tree/8cbdbbe6363510f7d9ceec685373da12e6fc752d/libssh2/out_of_bounds_read_disconnect_CVE-2019-17498
- https://github.com/libssh2/libssh2/blob/42d37aa63129a1b2644bf6495198923534322d64/src/packet.c#L480
- https://github.com/libssh2/libssh2/commit/dedcbd106f8e52d5586b0205bc7677e4c9868f9c
- https://lists.debian.org/debian-lts-announce/2019/11/msg00010.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00013.html
- https://lists.debian.org/debian-lts-announce/2023/09/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/22H4Q5XMGS3QNSA7OCL3U7UQZ4NXMR5O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TY7EEE34RFKCTXTMBQQWWSLXZWSCXNDB/
- https://security.netapp.com/advisory/ntap-20220909-0004/
