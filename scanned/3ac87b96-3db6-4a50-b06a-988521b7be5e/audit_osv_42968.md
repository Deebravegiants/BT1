# [H] selinux: avoid sk_socket dereference in selinux_sctp_bind_connect()

## Summary
Severity: High
Advisory: CVE-2026-72242
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72242
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

selinux: avoid sk_socket dereference in selinux_sctp_bind_connect()

selinux_sctp_bind_connect() dereferences sk->sk_socket to pass a
struct socket * to selinux_socket_bind() and
selinux_socket_connect_helper().  However, when the hook is invoked
from the ASCONF softirq path (sctp_process_asconf), there is no file
reference guaranteeing that sk->sk_socket is non-NULL.  The setsockopt
callers (bindx, connectx, set_primary, sendmsg connect) hold a file
reference and are not affected.

Both selinux_socket_bind() and selinux_socket_connect_helper()
immediately resolve sock->sk, never using the struct socket * for
anything else.  Refactor the inner logic into helpers that take a
struct sock * directly so that selinux_sctp_bind_connect() never needs
to touch sk->sk_socket at all.

## References
- https://git.kernel.org/stable/c/2fcaf133a8fd88b69f32ebaecad93fd302da828f
- https://git.kernel.org/stable/c/37d642b37ccdc31e1947c2ebc8dc38f03d4a0ceb
- https://git.kernel.org/stable/c/56acfeb10019e200ab6787d01f8d7cbe0f01526f
- https://git.kernel.org/stable/c/5d4d93f9bfbc997ffbb03cd6107e8f6979dbb9b4
- https://git.kernel.org/stable/c/a4bc2fb8536488b37680c0b66c59434a4b7f8c2f
- https://git.kernel.org/stable/c/cc8bd47b35eca82393cbad08b1cc86f02e034439
- https://git.kernel.org/stable/c/d61a80b17254be7230bc5544f8e62ddf21ab38e2
- https://git.kernel.org/stable/c/e4f3b8db1b0c5e9f6374b8996d9e1888d1042b55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72242.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
