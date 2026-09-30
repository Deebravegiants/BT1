# [H] sctp: diag: reject stale associations in dump_one path

## Summary
Severity: High
Advisory: CVE-2026-52917
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52917
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: diag: reject stale associations in dump_one path

The SCTP exact sock_diag lookup can hold a transport reference, block on
lock_sock(sk), and then resume after sctp_association_free() has marked
the association dead and freed its bind address list.

When that happens, inet_assoc_attr_size() and
inet_diag_msg_sctpasoc_fill() can still dereference association state
that is no longer valid for reporting. In particular,
inet_diag_msg_sctpasoc_fill() may read an empty bind-address list as a
real sctp_sockaddr_entry and trigger an out-of-bounds read from
unrelated association memory.

Reject the association after taking the socket lock if it has been
reaped or detached from the endpoint, and report the lookup as stale.
This keeps the exact dump-one path from formatting torn association
state.

## References
- https://git.kernel.org/stable/c/480f754580b5686b928977d16a59f20cef83ff01
- https://git.kernel.org/stable/c/5425de8bd6e9fe5bd67d158e3348171ae7510117
- https://git.kernel.org/stable/c/5eba3e48d78edd7551b992cb7ba687019b3a78da
- https://git.kernel.org/stable/c/6657af827e21883ae90693e42e7f59a6aab690b5
- https://git.kernel.org/stable/c/78c4f964b2f94e405721c093773f6250e1e676b2
- https://git.kernel.org/stable/c/b2be72d401833194917e44fbd8d8144bb4f2db16
- https://git.kernel.org/stable/c/e97c2a535e23ed0fdd2660993fb3f10d9535c9bc
- https://git.kernel.org/stable/c/f5af203dec6e0e7a6090fcc2130e9f3901bfc84d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52917.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52917
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
